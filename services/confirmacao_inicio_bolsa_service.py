"""Confirmação de início da bolsa: bolsista + orientador (após ativação FA)."""
import os
import re
from datetime import date

from flask import render_template
from sqlalchemy import or_

from audit import log_action
from core.datetime_utils import utc_now, format_datetime_br
from extensions import db
from models import Bolsista, SistemaConfig, ComentarioBolsista
from utils.date_utils import format_date_br
from utils.email_sender import send_email

CONFIG_KEY_CORPO = 'inicio_bolsa_email_corpo'
CONFIG_KEY_EQUIPE = 'inicio_bolsa_email_equipe'

DEFAULT_CORPO_EMAIL = """Confirmamos o início da sua participação como bolsista no projeto NAPI-Robótica.

As datas, a quantidade de parcelas e o edital constam abaixo. Pedimos que bolsista e orientador(a)/supervisor(a) confirmem estes dados respondendo a este e-mail. Se houver divergência, respondam o mais breve possível."""


def _get_config(chave):
    row = SistemaConfig.query.get(chave)
    return row.valor.strip() if row and row.valor else None


def _set_config(chave, valor):
    row = SistemaConfig.query.get(chave)
    if not row:
        db.session.add(SistemaConfig(chave=chave, valor=valor))
    else:
        row.valor = valor


def _logo_url_preview():
    from flask import has_request_context, url_for

    if has_request_context():
        return url_for('static', filename='images/napi_robotica_logo.png', _external=True)
    base = (os.getenv('BASE_URL') or '').rstrip('/')
    if base:
        return f'{base}/static/images/napi_robotica_logo.png'
    return '/static/images/napi_robotica_logo.png'


class ConfirmacaoInicioBolsaService:
    @classmethod
    def reply_email(cls):
        return os.getenv(
            'INICIO_BOLSA_REPLY_EMAIL',
            os.getenv('MAIL_DEFAULT_SENDER', 'robotica-ct@utfpr.edu.br'),
        ).strip()

    @classmethod
    def get_email_body_raw(cls):
        return _get_config(CONFIG_KEY_CORPO) or DEFAULT_CORPO_EMAIL

    @classmethod
    def get_equipe_email_raw(cls):
        val = _get_config(CONFIG_KEY_EQUIPE)
        if val:
            return val
        return os.getenv(
            'INICIO_BOLSA_EQUIPE_EMAIL',
            os.getenv('NOTIFICATION_EMAIL', cls.reply_email()),
        ).strip()

    @classmethod
    def get_equipe_recipients(cls):
        parts = re.split(r'[;,\s]+', cls.get_equipe_email_raw())
        return [p.strip() for p in parts if p.strip() and '@' in p]

    @classmethod
    def save_config(cls, corpo_text, equipe_emails):
        corpo_text = (corpo_text or '').strip()
        equipe_emails = (equipe_emails or '').strip()
        if not corpo_text:
            return False, 'Informe o texto do e-mail de confirmação.'
        if not equipe_emails:
            return False, 'Informe o e-mail da equipe Robótica (resumo).'
        recipients = [p.strip() for p in re.split(r'[;,\n]+', equipe_emails) if p.strip()]
        if not any('@' in r for r in recipients):
            return False, 'E-mail da equipe inválido.'
        _set_config(CONFIG_KEY_CORPO, corpo_text)
        _set_config(CONFIG_KEY_EQUIPE, '; '.join(recipients))
        db.session.commit()
        return True, 'Configuração de confirmação de início salva.'

    @classmethod
    def email_body_to_html(cls, texto):
        partes = [p.strip() for p in (texto or '').split('\n\n') if p.strip()]
        if not partes:
            partes = [DEFAULT_CORPO_EMAIL]
        return ''.join(
            f'<p style="margin:0 0 1rem;">{p.replace(chr(10), "<br>")}</p>' for p in partes
        )

    @classmethod
    def calcular_vigencia(cls, bolsista, data_inicio=None):
        from services.bolsista_service import BolsistaService

        inicio = data_inicio or bolsista.data_inicio_bolsa
        meses = bolsista.meses_duracao
        fim = None
        if inicio and meses:
            afastamentos = []
            if getattr(bolsista, 'afastamentos', None):
                afastamentos = [
                    {'tipo': a.tipo, 'duracao_meses': a.duracao_meses}
                    for a in bolsista.afastamentos
                ]
            fim = BolsistaService.calculate_end_date(inicio, meses, afastamentos)
        return inicio, fim, meses or 0

    @classmethod
    def _destinatarios(cls, bolsista):
        emails = []
        for addr in (bolsista.email, bolsista.email_orientador):
            a = (addr or '').strip()
            if a and '@' in a and a.lower() not in {e.lower() for e in emails}:
                emails.append(a)
        return emails

    @classmethod
    def _cc_equipe(cls, recipients=None):
        """Cópia para a secretaria Robótica, sem duplicar quem já está em Para."""
        dest = {e.lower() for e in (recipients or [])}
        cc = []
        for addr in cls.get_equipe_recipients():
            key = addr.lower()
            if key not in dest and key not in {e.lower() for e in cc}:
                cc.append(addr)
        return cc

    @classmethod
    def _valor_mensal_fmt(cls, bolsista):
        valor = bolsista.modalidade.valor_mensal if bolsista.modalidade else None
        if valor is None:
            return None
        try:
            return f'R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
        except Exception:
            return str(valor)

    @classmethod
    def _build_message(cls, bolsista, data_inicio=None, for_preview=False, corpo_text=None):
        inicio, fim, parcelas = cls.calcular_vigencia(bolsista, data_inicio=data_inicio)
        edital_numero = bolsista.edital.numero if bolsista.edital else '-'
        reply = cls.reply_email()
        corpo_texto = corpo_text if corpo_text is not None else cls.get_email_body_raw()
        subject = f'NAPI-Robótica — Confirmação de início da bolsa: {bolsista.nome}'
        html = render_template(
            'emails/confirmacao_inicio_bolsa.html',
            bolsista=bolsista,
            edital_numero=edital_numero,
            reply_email=reply,
            data_inicio=inicio,
            data_fim=fim,
            total_parcelas=parcelas,
            valor_mensal=cls._valor_mensal_fmt(bolsista),
            corpo_html=cls.email_body_to_html(corpo_texto),
            logo_src=_logo_url_preview() if for_preview else 'cid:napi_logo',
        )
        text_body = (
            f'{corpo_texto}\n\n'
            f'---\nBolsista: {bolsista.nome}\n'
            f'Edital: {edital_numero}\n'
            f'Orientador(a): {bolsista.orientador or "-"}\n'
            f'Início: {format_date_br(inicio) or "-"}\n'
            f'Fim: {format_date_br(fim) or "-"}\n'
            f'Parcelas: {parcelas}\n'
            f'Contato: {reply}'
        )
        recipients = cls._destinatarios(bolsista)
        return subject, html, text_body, {
            'inicio': inicio,
            'fim': fim,
            'parcelas': parcelas,
            'recipients': recipients,
            'cc': cls._cc_equipe(recipients),
        }

    @classmethod
    def render_preview_html(cls, bolsista=None, data_inicio=None, corpo_text=None):
        from types import SimpleNamespace

        if bolsista is None:
            bolsista = SimpleNamespace(
                nome='Nome do Bolsista (exemplo)',
                email='bolsista@exemplo.edu.br',
                orientador='Orientador(a) Exemplo',
                email_orientador='orientador@exemplo.edu.br',
                meses_duracao=12,
                data_inicio_bolsa=date.today(),
                edital=SimpleNamespace(numero='03/2026'),
                modalidade=SimpleNamespace(valor_mensal=1500),
                afastamentos=[],
            )
            data_inicio = data_inicio or date.today()
        _subject, html, _text, meta = cls._build_message(
            bolsista, data_inicio=data_inicio, for_preview=True, corpo_text=corpo_text
        )
        return html, meta, _subject

    @classmethod
    def is_elegivel(cls, bolsista, forcar=False):
        if not bolsista.ativo:
            return False
        if getattr(bolsista, 'implantacao_pendente', False):
            return False
        if getattr(bolsista, 'status_governanca', None) == 'PENDENTE':
            return False
        if not bolsista.data_inicio_bolsa or not bolsista.meses_duracao:
            return False
        if not cls._destinatarios(bolsista):
            return False
        if forcar:
            return True
        return not bolsista.inicio_email_enviado_em

    @classmethod
    def listar_elegiveis(cls, forcar=False):
        candidatos = (
            Bolsista.query.filter(
                Bolsista.ativo == True,
                Bolsista.data_inicio_bolsa.isnot(None),
                Bolsista.meses_duracao.isnot(None),
                or_(Bolsista.implantacao_pendente == False, Bolsista.implantacao_pendente.is_(None)),
                or_(
                    Bolsista.status_governanca.is_(None),
                    Bolsista.status_governanca != 'PENDENTE',
                ),
            )
            .order_by(Bolsista.nome)
            .all()
        )
        return [b for b in candidatos if cls.is_elegivel(b, forcar=forcar)]

    @classmethod
    def _registrar_comentario(cls, bolsista, recipients, inicio, fim, parcelas, user_id=None):
        dest = ', '.join(recipients) if recipients else '—'
        texto = (
            '[CONFIRMAÇÃO DE INÍCIO DA BOLSA]\n'
            f'E-mail enviado em {format_datetime_br(utc_now())}.\n'
            f'Vigência: {format_date_br(inicio) or "—"} a {format_date_br(fim) or "—"} '
            f'({parcelas} parcela(s)).\n'
            f'Destinatários: {dest}'
        )
        bolsista.comentarios_historico.append(
            ComentarioBolsista(texto=texto, user_id=user_id)
        )

    @classmethod
    def enviar_individual(cls, bolsista, dry_run=False, forcar=False, user_id=None, data_inicio=None):
        if not cls.is_elegivel(bolsista, forcar=forcar) and not dry_run:
            if bolsista.inicio_email_enviado_em and not forcar:
                return False, 'Confirmação de início já enviada.'
            return False, 'Bolsista não elegível para confirmação de início.'

        recipients = cls._destinatarios(bolsista)
        if not recipients:
            return False, f'Sem e-mail do bolsista ou orientador para {bolsista.nome}.'

        subject, html, text_body, meta = cls._build_message(
            bolsista, data_inicio=data_inicio or bolsista.data_inicio_bolsa
        )
        cc = meta.get('cc') or cls._cc_equipe(recipients)
        if dry_run:
            copia = f' (CC {", ".join(cc)})' if cc else ''
            return True, f'[DRY-RUN] confirmação início → {", ".join(recipients)}{copia}'

        send_email(subject, recipients, html, text_body=text_body, cc=cc or None)
        bolsista.inicio_email_enviado_em = utc_now()
        dest_hist = recipients + ([f'CC: {a}' for a in cc] if cc else [])
        cls._registrar_comentario(
            bolsista, dest_hist, meta['inicio'], meta['fim'], meta['parcelas'], user_id=user_id
        )
        db.session.commit()
        log_action(
            'INICIO_BOLSA_CONFIRMACAO',
            tabela='bolsistas',
            registro_id=bolsista.id,
            detalhes=(
                f"Início: {format_date_br(meta['inicio'])}; "
                f"Fim: {format_date_br(meta['fim'])}; "
                f"Parcelas: {meta['parcelas']}; Para: {', '.join(recipients)}"
                + (f"; CC: {', '.join(cc)}" if cc else '')
            ),
        )
        copia = f' (cópia: {", ".join(cc)})' if cc else ''
        return True, f'Confirmação de início enviada para {", ".join(recipients)}{copia}.'

    @classmethod
    def enviar_resumo_equipe(cls, enviados, hoje=None, dry_run=False):
        hoje = hoje or date.today()
        if not enviados:
            return False, None
        recipients = cls.get_equipe_recipients()
        if not recipients:
            return False, 'Configure o e-mail da equipe Robótica.'
        subject = (
            f'NAPI-Robótica — {len(enviados)} confirmação(ões) de início de bolsa — '
            f'{hoje.strftime("%d/%m/%Y")}'
        )
        html = render_template(
            'emails/confirmacao_inicio_bolsa_resumo.html',
            enviados=enviados,
            data_ref=hoje,
        )
        linhas = []
        for b in enviados:
            linhas.append(
                f'- {b.nome} | Edital: {(b.edital.numero if b.edital else "-")} | '
                f'Início: {format_date_br(b.data_inicio_bolsa)} | '
                f'Fim: {format_date_br(b.data_fim_bolsa)} | '
                f'Parcelas: {b.meses_duracao or "-"}'
            )
        text_body = (
            f'Confirmações de início enviadas ({len(enviados)}) em '
            f'{hoje.strftime("%d/%m/%Y")}:\n\n' + '\n'.join(linhas)
        )
        if dry_run:
            return True, f'[DRY-RUN] Resumo equipe → {", ".join(recipients)} ({len(enviados)})'
        send_email(subject, recipients, html, text_body=text_body)
        log_action(
            'INICIO_BOLSA_RESUMO',
            tabela='bolsistas',
            registro_id=None,
            detalhes=f"Para: {', '.join(recipients)}; {len(enviados)} aviso(s)",
        )
        return True, f'Resumo enviado para {", ".join(recipients)} ({len(enviados)} aviso(s)).'

    @classmethod
    def processar_diario(cls, dry_run=False, forcar=False):
        """Rede de segurança: ativos implantados sem o e-mail de confirmação."""
        from models import LogAutomacao

        log = None if dry_run else LogAutomacao(nome_tarefa='Confirmação Início de Bolsa')
        try:
            elegiveis = cls.listar_elegiveis(forcar=forcar)
            if not elegiveis:
                result = {
                    'ok': True,
                    'enviados': 0,
                    'message': 'Nenhum bolsista pendente de confirmação de início.',
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
                    ok, msg = cls.enviar_individual(b, dry_run=dry_run, forcar=forcar)
                    if ok:
                        enviados_objs.append(b)
                        detalhes.append(f'{b.nome}: {msg}')
                    else:
                        erros.append(f'{b.nome}: {msg}')
                except Exception as e:
                    erros.append(f'{b.nome}: {e}')

            resumo_ok, resumo_msg = cls.enviar_resumo_equipe(enviados_objs, dry_run=dry_run)
            if resumo_ok and resumo_msg:
                detalhes.append(resumo_msg)

            result = {
                'ok': len(erros) == 0,
                'enviados': len(enviados_objs),
                'erros': erros,
                'detalhes': detalhes,
                'message': (
                    f'Confirmação de início: {len(enviados_objs)} enviado(s), '
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
