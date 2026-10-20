"""Aviso automático: último mês de vigência da bolsa (bolsista + orientador)."""
import os
import re
from datetime import date

from flask import render_template
from sqlalchemy import extract, or_

from audit import log_action
from core.datetime_utils import utc_now, format_datetime_br
from core.status_engine import StatusEngine, BolsistaStatus
from extensions import db
from models import Bolsista, SistemaConfig, ComentarioBolsista
from utils.date_utils import calcular_parcelas, format_date_br
from utils.email_sender import send_email

CONFIG_KEY_CORPO = 'ultimo_mes_email_corpo'
CONFIG_KEY_EQUIPE = 'ultimo_mes_email_equipe'

DEFAULT_CORPO_EMAIL = """Informamos que este é o último mês de vigência da bolsa no projeto NAPI-Robótica.

Orientador(a)/supervisor(a) e bolsista: providenciem o encerramento das atividades, a documentação de checkout e, após o desligamento, o envio do relatório final conforme orientações da secretaria.

Qualquer dúvida, responda a este e-mail."""


def _get_config(chave):
    row = SistemaConfig.query.get(chave)
    return row.valor.strip() if row and row.valor else None


def _set_config(chave, valor):
    row = SistemaConfig.query.get(chave)
    if not row:
        db.session.add(SistemaConfig(chave=chave, valor=valor))
    else:
        row.valor = valor


class UltimoMesBolsaService:
    @classmethod
    def reply_email(cls):
        return os.getenv(
            'ULTIMO_MES_REPLY_EMAIL',
            os.getenv('MAIL_DEFAULT_SENDER', 'robotica-ct@utfpr.edu.br'),
        ).strip()

    @classmethod
    def get_email_body_raw(cls):
        val = _get_config(CONFIG_KEY_CORPO)
        return val if val else DEFAULT_CORPO_EMAIL

    @classmethod
    def get_equipe_email_raw(cls):
        val = _get_config(CONFIG_KEY_EQUIPE)
        if val:
            return val
        return os.getenv(
            'ULTIMO_MES_EQUIPE_EMAIL',
            os.getenv('NOTIFICATION_EMAIL', cls.reply_email()),
        ).strip()

    @classmethod
    def get_equipe_recipients(cls):
        raw = cls.get_equipe_email_raw()
        parts = re.split(r'[;,\s]+', raw)
        return [p.strip() for p in parts if p.strip() and '@' in p]

    @classmethod
    def save_config(cls, corpo_text, equipe_emails):
        corpo_text = (corpo_text or '').strip()
        equipe_emails = (equipe_emails or '').strip()
        if not corpo_text:
            return False, 'Informe o texto do e-mail de aviso.'
        if not equipe_emails:
            return False, 'Informe o e-mail da equipe Robótica (resumo).'
        recipients = [p.strip() for p in re.split(r'[;,\n]+', equipe_emails) if p.strip()]
        if not any('@' in r for r in recipients):
            return False, 'E-mail da equipe inválido.'
        _set_config(CONFIG_KEY_CORPO, corpo_text)
        _set_config(CONFIG_KEY_EQUIPE, '; '.join(recipients))
        db.session.commit()
        return True, 'Configuração de aviso do último mês salva.'

    @classmethod
    def email_body_to_html(cls, texto):
        partes = [p.strip() for p in (texto or '').split('\n\n') if p.strip()]
        if not partes:
            partes = [DEFAULT_CORPO_EMAIL]
        return ''.join(
            f'<p style="margin:0 0 1rem;">{p.replace(chr(10), "<br>")}</p>' for p in partes
        )

    @classmethod
    def competencia_fim(cls, bolsista):
        if not bolsista.data_fim_bolsa:
            return None
        return bolsista.data_fim_bolsa.strftime('%Y-%m')

    @classmethod
    def _destinatarios(cls, bolsista):
        emails = []
        for addr in (bolsista.email, bolsista.email_orientador):
            a = (addr or '').strip()
            if a and '@' in a and a.lower() not in {e.lower() for e in emails}:
                emails.append(a)
        return emails

    @classmethod
    def _parcela_info(cls, bolsista, hoje=None):
        hoje = hoje or date.today()
        ref = hoje.replace(day=1)
        parcela = calcular_parcelas(bolsista.data_inicio_bolsa, ref)
        total = bolsista.meses_duracao or 0
        return parcela, total

    @classmethod
    def is_elegivel(cls, bolsista, hoje=None, forcar=False):
        hoje = hoje or date.today()
        if not bolsista.ativo:
            return False
        if getattr(bolsista, 'implantacao_pendente', False):
            return False
        if getattr(bolsista, 'status_governanca', None) == 'PENDENTE':
            return False
        if not bolsista.data_fim_bolsa:
            return False
        # Mês-calendário do fim (mesmo critério de ULTIMA_PARCELA; inclui SUSPENSO)
        if (
            bolsista.data_fim_bolsa.month != hoje.month
            or bolsista.data_fim_bolsa.year != hoje.year
        ):
            return False
        status = StatusEngine.get_status(bolsista)
        if status in (
            BolsistaStatus.INATIVO,
            BolsistaStatus.PENDENTE_GOVERNANCA,
            BolsistaStatus.AGUARDANDO_IMPLANTACAO,
            BolsistaStatus.CANCELAMENTO_REQUERIDO,
            BolsistaStatus.VENCIDO_CRITICO,
        ):
            return False
        if not cls._destinatarios(bolsista):
            return False
        if forcar:
            return True
        competencia = cls.competencia_fim(bolsista)
        return bolsista.ultimo_mes_email_competencia != competencia

    @classmethod
    def listar_elegiveis(cls, hoje=None, forcar=False):
        hoje = hoje or date.today()
        candidatos = (
            Bolsista.query.filter(
                Bolsista.ativo == True,
                Bolsista.data_fim_bolsa.isnot(None),
                extract('month', Bolsista.data_fim_bolsa) == hoje.month,
                extract('year', Bolsista.data_fim_bolsa) == hoje.year,
            )
            .order_by(Bolsista.nome)
            .all()
        )
        return [b for b in candidatos if cls.is_elegivel(b, hoje=hoje, forcar=forcar)]

    @classmethod
    def _registrar_comentario(cls, bolsista, recipients, parcela, total, user_id=None):
        competencia = cls.competencia_fim(bolsista) or '—'
        fim_txt = format_date_br(bolsista.data_fim_bolsa) or '—'
        dest = ', '.join(recipients) if recipients else '—'
        texto = (
            f'[AVISO ÚLTIMO MÊS DE BOLSA]\n'
            f'E-mail de aviso do último mês de bolsa enviado em {format_datetime_br(utc_now())}.\n'
            f'Competência: {competencia} | Fim previsto da bolsa: {fim_txt} | '
            f'Parcela: {parcela}/{total}\n'
            f'Destinatários: {dest}'
        )
        bolsista.comentarios_historico.append(
            ComentarioBolsista(texto=texto, user_id=user_id)
        )

    @classmethod
    def enviar_aviso_individual(cls, bolsista, dry_run=False, forcar=False, user_id=None):
        hoje = date.today()
        if not cls.is_elegivel(bolsista, hoje=hoje, forcar=forcar):
            return False, 'Bolsista não elegível para aviso do último mês.'

        recipients = cls._destinatarios(bolsista)
        if not recipients:
            return False, f'Sem e-mail do bolsista ou orientador para {bolsista.nome}.'

        parcela, total = cls._parcela_info(bolsista, hoje)
        edital_numero = bolsista.edital.numero if bolsista.edital else '-'
        reply = cls.reply_email()
        corpo_texto = cls.get_email_body_raw()
        competencia = cls.competencia_fim(bolsista)
        subject = f'NAPI-Robótica — Último mês de bolsa: {bolsista.nome}'

        html = render_template(
            'emails/aviso_ultimo_mes_bolsa.html',
            bolsista=bolsista,
            edital_numero=edital_numero,
            reply_email=reply,
            data_fim=bolsista.data_fim_bolsa,
            parcela=parcela,
            total_parcelas=total,
            corpo_html=cls.email_body_to_html(corpo_texto),
        )
        text_body = (
            f'{corpo_texto}\n\n'
            f'---\nBolsista: {bolsista.nome}\n'
            f'Edital: {edital_numero}\n'
            f'Orientador(a): {bolsista.orientador or "-"}\n'
            f'Fim da bolsa: {format_date_br(bolsista.data_fim_bolsa)}\n'
            f'Parcela: {parcela}/{total}\n'
            f'Contato: {reply}'
        )

        if dry_run:
            return True, f'[DRY-RUN] último mês → {", ".join(recipients)}'

        send_email(subject, recipients, html, text_body=text_body)
        bolsista.ultimo_mes_email_enviado_em = utc_now()
        bolsista.ultimo_mes_email_competencia = competencia
        cls._registrar_comentario(bolsista, recipients, parcela, total, user_id=user_id)
        db.session.commit()

        log_action(
            'ULTIMO_MES_BOLSA_EMAIL',
            tabela='bolsistas',
            registro_id=bolsista.id,
            detalhes=f"Competência: {competencia}; Para: {', '.join(recipients)}",
        )
        return True, f'Aviso último mês enviado para {", ".join(recipients)}.'

    @classmethod
    def enviar_resumo_equipe(cls, enviados, hoje=None, dry_run=False):
        hoje = hoje or date.today()
        if not enviados:
            return False, None

        recipients = cls.get_equipe_recipients()
        if not recipients:
            return False, 'Configure o e-mail da equipe Robótica.'

        subject = (
            f'NAPI-Robótica — {len(enviados)} bolsista(s) no último mês de bolsa — '
            f'{hoje.strftime("%d/%m/%Y")}'
        )
        html = render_template(
            'emails/aviso_ultimo_mes_bolsa_resumo.html',
            enviados=enviados,
            data_ref=hoje,
        )
        linhas = []
        for b in enviados:
            linhas.append(
                f'- {b.nome} | Edital: {(b.edital.numero if b.edital else "-")} | '
                f'Fim: {format_date_br(b.data_fim_bolsa)} | '
                f'Bolsista: {b.email or "sem e-mail"} | Orientador: {b.email_orientador or "sem e-mail"}'
            )
        text_body = (
            f'Bolsistas no último mês de vigência ({len(enviados)}) em '
            f'{hoje.strftime("%d/%m/%Y")}:\n\n' + '\n'.join(linhas)
        )

        if dry_run:
            return True, f'[DRY-RUN] Resumo equipe → {", ".join(recipients)} ({len(enviados)})'

        send_email(subject, recipients, html, text_body=text_body)
        log_action(
            'ULTIMO_MES_BOLSA_RESUMO',
            tabela='bolsistas',
            registro_id=None,
            detalhes=f"Para: {', '.join(recipients)}; {len(enviados)} aviso(s)",
        )
        return True, f'Resumo enviado para {", ".join(recipients)} ({len(enviados)} aviso(s)).'

    @classmethod
    def sincronizar_apos_mudanca_fim(cls, bolsista, fim_anterior):
        """
        Se o mês/ano de data_fim_bolsa mudou, limpa o controle de aviso
        para permitir novo envio na competência correta.
        """
        nova = cls.competencia_fim(bolsista)
        antiga = fim_anterior.strftime('%Y-%m') if fim_anterior else None
        if nova == antiga:
            return False
        if bolsista.ultimo_mes_email_competencia and bolsista.ultimo_mes_email_competencia != nova:
            bolsista.ultimo_mes_email_competencia = None
            bolsista.ultimo_mes_email_enviado_em = None
            return True
        if antiga and not nova:
            bolsista.ultimo_mes_email_competencia = None
            bolsista.ultimo_mes_email_enviado_em = None
            return True
        return False

    @classmethod
    def contar_pendentes_aviso(cls, hoje=None):
        """Quantidade aproximada de ativos no último mês ainda sem aviso nesta competência."""
        hoje = hoje or date.today()
        comp = hoje.strftime('%Y-%m')
        return (
            Bolsista.query.filter(
                Bolsista.ativo == True,
                Bolsista.data_fim_bolsa.isnot(None),
                extract('month', Bolsista.data_fim_bolsa) == hoje.month,
                extract('year', Bolsista.data_fim_bolsa) == hoje.year,
                or_(
                    Bolsista.ultimo_mes_email_competencia.is_(None),
                    Bolsista.ultimo_mes_email_competencia != comp,
                ),
            ).count()
        )

    @classmethod
    def processar_diario(cls, dry_run=False, forcar=False):
        """Envia avisos a elegíveis no mês corrente (idempotente por competência)."""
        from models import LogAutomacao

        hoje = date.today()
        log = None if dry_run else LogAutomacao(nome_tarefa='Aviso Último Mês de Bolsa')

        try:
            elegiveis = cls.listar_elegiveis(hoje=hoje, forcar=forcar)

            if not elegiveis:
                result = {
                    'ok': True,
                    'enviados': 0,
                    'message': 'Nenhum bolsista elegível para aviso do último mês.',
                }
                if log:
                    log.status = 'SUCESSO'
                    log.mensagem = result['message']
                    log.registros_processados = 0
                return result

            enviados_objs = []
            erros = []
            detalhes = []

            for b in elegiveis:
                try:
                    ok, msg = cls.enviar_aviso_individual(b, dry_run=dry_run, forcar=forcar)
                    if ok:
                        enviados_objs.append(b)
                        detalhes.append(f'{b.nome}: {msg}')
                    else:
                        erros.append(f'{b.nome}: {msg}')
                except Exception as e:
                    erros.append(f'{b.nome}: {e}')

            resumo_ok, resumo_msg = cls.enviar_resumo_equipe(
                enviados_objs, hoje=hoje, dry_run=dry_run
            )
            if resumo_ok and resumo_msg:
                detalhes.append(resumo_msg)

            result = {
                'ok': len(erros) == 0,
                'enviados': len(enviados_objs),
                'erros': erros,
                'detalhes': detalhes,
                'message': (
                    f'Aviso último mês: {len(enviados_objs)} enviado(s), '
                    f'resumo equipe: {"sim" if resumo_ok else "não"}.'
                ),
            }
            if log:
                log.status = 'SUCESSO' if result['ok'] else 'ERRO'
                log.mensagem = result['message']
                if erros:
                    log.mensagem += ' | ' + '; '.join(erros[:5])
                log.registros_processados = len(enviados_objs)
            return result
        except Exception as e:
            if log:
                log.status = 'ERRO'
                log.mensagem = str(e)
                log.registros_processados = 0
            raise
        finally:
            if log:
                db.session.add(log)
                db.session.commit()
