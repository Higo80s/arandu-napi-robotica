"""Cobrança de relatório final: desligamento imediato + lembrete mensal (dia 15)."""
import os
import re
from datetime import date

from flask import render_template
from sqlalchemy import or_

from audit import log_action
from core.datetime_utils import utc_now, format_datetime_br
from extensions import db
from models import Bolsista, SistemaConfig, ComentarioBolsista
from utils.email_sender import send_email

DEFAULT_MODELO_URL = 'https://nuvem.utfpr.edu.br/index.php/s/owE52McFwGeVnI1'
CONFIG_KEY_CORPO = 'relatorio_final_email_corpo'
CONFIG_KEY_EQUIPE = 'relatorio_final_email_equipe'

DEFAULT_CORPO_EMAIL = """Informamos que o vínculo como bolsista no projeto NAPI-Robótica foi encerrado.

Mesmo em caso de desligamento antecipado, é obrigatório o envio do Relatório Final de Estágio ao projeto.

Baixe o modelo pelo link indicado abaixo, preencha o documento e envie respondendo a este e-mail ou para a secretaria do projeto.

Orientador(a)/supervisor(a): favor acompanhar o(a) bolsista quanto ao cumprimento desta exigência."""


def _get_config(chave):
    row = SistemaConfig.query.get(chave)
    return row.valor.strip() if row and row.valor else None


def _set_config(chave, valor):
    row = SistemaConfig.query.get(chave)
    if not row:
        db.session.add(SistemaConfig(chave=chave, valor=valor))
    else:
        row.valor = valor


class RelatorioFinalService:
    @classmethod
    def modelo_url(cls):
        return os.getenv('RELATORIO_FINAL_MODELO_URL', DEFAULT_MODELO_URL).strip()

    @classmethod
    def reply_email(cls):
        return os.getenv(
            'RELATORIO_FINAL_REPLY_EMAIL',
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
            'RELATORIO_FINAL_EQUIPE_EMAIL',
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
            return False, 'Informe o texto do e-mail de cobrança.'
        if not equipe_emails:
            return False, 'Informe o e-mail da equipe Robótica (resumo mensal).'
        recipients = [p.strip() for p in re.split(r'[;,\n]+', equipe_emails) if p.strip()]
        if not any('@' in r for r in recipients):
            return False, 'E-mail da equipe inválido.'
        _set_config(CONFIG_KEY_CORPO, corpo_text)
        _set_config(CONFIG_KEY_EQUIPE, '; '.join(recipients))
        db.session.commit()
        return True, 'Configuração de cobrança de relatório final salva.'

    @classmethod
    def email_body_to_html(cls, texto):
        partes = [p.strip() for p in (texto or '').split('\n\n') if p.strip()]
        if not partes:
            partes = [DEFAULT_CORPO_EMAIL]
        return ''.join(
            f'<p style="margin:0 0 1rem;">{p.replace(chr(10), "<br>")}</p>' for p in partes
        )

    @classmethod
    def data_referencia_desligamento(cls, bolsista):
        return bolsista.data_desligamento or bolsista.data_fim_bolsa

    @classmethod
    def _filtros_pendentes(cls):
        """Inativos de fato (desligados). Exclui cadastro aguardando implantação/FUNTEF.

        ``ativo=False`` sozinho pega quem ainda não foi ativado pela Fundação
        (ver ImplantacaoBolsaService.marcar_pendente). Esses aparecem no painel
        como "Aguardando implantação" e não devem receber cobrança de relatório.
        Alinha com Bolsista.cobranca_relatorio_pendente.
        """
        return (
            Bolsista.ativo == False,
            or_(Bolsista.relatorio_entregue == False, Bolsista.relatorio_entregue.is_(None)),
            or_(Bolsista.implantacao_pendente == False, Bolsista.implantacao_pendente.is_(None)),
            or_(
                Bolsista.status_governanca.is_(None),
                Bolsista.status_governanca != 'PENDENTE',
            ),
        )

    @classmethod
    def listar_pendentes(cls):
        return (
            Bolsista.query.filter(*cls._filtros_pendentes())
            .order_by(Bolsista.nome)
            .all()
        )

    @classmethod
    def motivo_nao_elegivel(cls, bolsista):
        if bolsista.relatorio_entregue:
            return 'Relatório já entregue.'
        if bolsista.ativo:
            return 'Bolsista ativo — cobrança só após desligamento.'
        if getattr(bolsista, 'implantacao_pendente', False) or (
            getattr(bolsista, 'status_governanca', None) == 'PENDENTE'
        ):
            return (
                'Cadastro ainda não implantado (aguardando ativação da Fundação); '
                'não há cobrança de relatório final.'
            )
        if not getattr(bolsista, 'cobranca_relatorio_pendente', False):
            return 'Bolsista não elegível para cobrança de relatório final.'
        return None

    @classmethod
    def _destinatarios_cobranca(cls, bolsista):
        emails = []
        for addr in (bolsista.email, bolsista.email_orientador):
            a = (addr or '').strip()
            if a and '@' in a and a.lower() not in {e.lower() for e in emails}:
                emails.append(a)
        return emails

    @classmethod
    def _build_message(cls, bolsista, motivo):
        modelo_url = cls.modelo_url()
        reply = cls.reply_email()
        edital_numero = bolsista.edital.numero if bolsista.edital else '-'
        ref = cls.data_referencia_desligamento(bolsista)
        corpo_texto = cls.get_email_body_raw()

        if motivo == 'desligamento':
            subject = f'NAPI-Robótica — Relatório final obrigatório (desligamento): {bolsista.nome}'
        else:
            subject = f'NAPI-Robótica — Lembrete: relatório final pendente — {bolsista.nome}'

        html = render_template(
            'emails/cobranca_relatorio_final.html',
            bolsista=bolsista,
            edital_numero=edital_numero,
            modelo_url=modelo_url,
            reply_email=reply,
            data_desligamento=ref,
            corpo_html=cls.email_body_to_html(corpo_texto),
            motivo=motivo,
        )
        text_body = (
            f'{corpo_texto}\n\n'
            f'---\nBolsista: {bolsista.nome}\n'
            f'Edital: {edital_numero}\n'
            f'Orientador(a): {bolsista.orientador or "-"}\n'
            f'Data desligamento: {ref.strftime("%d/%m/%Y") if ref else "-"}\n'
            f'Modelo: {modelo_url}\n'
            f'Enviar para: {reply}'
        )
        return subject, html, text_body

    @classmethod
    def _registrar_comentario_cobranca(cls, bolsista, motivo, recipients, user_id=None):
        """Histórico de comentários: registro de cada e-mail de cobrança enviado."""
        if motivo == 'desligamento':
            titulo = 'COBRANÇA RELATÓRIO — desligamento'
        else:
            titulo = 'COBRANÇA RELATÓRIO — lembrete mensal (dia 15)'
        dest = ', '.join(recipients) if recipients else '—'
        texto = (
            f'[{titulo}]\n'
            f'E-mail de cobrança do relatório final enviado em {format_datetime_br(utc_now())}.\n'
            f'Destinatários: {dest}'
        )
        bolsista.comentarios_historico.append(
            ComentarioBolsista(texto=texto, user_id=user_id)
        )

    @classmethod
    def enviar_retificacao(cls, bolsista, dry_run=False, user_id=None):
        """Avisa bolsista/orientador para desconsiderar cobrança enviada por engano."""
        recipients = cls._destinatarios_cobranca(bolsista)
        if not recipients:
            return False, f'Sem e-mail do bolsista ou orientador para {bolsista.nome}.'

        reply = cls.reply_email()
        subject = (
            f'NAPI-Robótica — Desconsiderar e-mail anterior (relatório final): {bolsista.nome}'
        )
        html = render_template(
            'emails/retificacao_cobranca_relatorio.html',
            bolsista=bolsista,
            reply_email=reply,
        )
        text_body = (
            f'Prezado(a) {bolsista.nome},\n\n'
            'Enviamos hoje, por engano, um e-mail automático de cobrança de relatório final. '
            'Pedimos que desconsidere essa mensagem.\n\n'
            'Foi um teste automático do sistema. Não há pendência de relatório final nem '
            'desligamento associado a este cadastro. Nenhuma ação é necessária da sua parte.\n\n'
            'O cadastro permanece em implantação / aguardando ativação da bolsa. '
            'Pedimos desculpas pelo transtorno.\n\n'
            f'Em caso de dúvida: {reply}\n\n'
            'Atenciosamente,\nSecretaria do Projeto NAPI-Robótica — UTFPR'
        )

        if dry_run:
            return True, f'[DRY-RUN] retificação → {", ".join(recipients)}'

        from flask_mail import Message
        from extensions import mail
        from utils.email_sender import _enable_related_inline, _inline_parts_for_message

        msg = Message(subject, recipients=recipients)
        msg.html = html
        msg.body = text_body
        sender = os.getenv('MAIL_DEFAULT_SENDER')
        if sender:
            msg.sender = sender
        inline_parts = _inline_parts_for_message(html, None)
        if inline_parts:
            _enable_related_inline(msg, inline_parts)
        mail.send(msg)

        dest = ', '.join(recipients)
        bolsista.comentarios_historico.append(
            ComentarioBolsista(
                texto=(
                    '[RETIFICAÇÃO RELATÓRIO FINAL]\n'
                    f'E-mail de retratação enviado em {format_datetime_br(utc_now())}.\n'
                    'Motivo: cobrança disparada por teste automático / cadastro ainda em implantação. '
                    'O destinatário deve desconsiderar o aviso anterior.\n'
                    f'Destinatários: {dest}'
                ),
                user_id=user_id,
            )
        )
        db.session.commit()
        log_action(
            'RELATORIO_FINAL_RETIFICACAO',
            tabela='bolsistas',
            registro_id=bolsista.id,
            detalhes=f'Para: {dest}',
        )
        return True, f'Retificação enviada para {dest}.'

    @classmethod
    def enviar_cobranca_individual(cls, bolsista, motivo='mensal', dry_run=False, user_id=None):
        recusa = cls.motivo_nao_elegivel(bolsista)
        if recusa:
            return False, recusa

        if motivo == 'mensal' and bolsista.relatorio_ultima_cobranca_em:
            ultima = bolsista.relatorio_ultima_cobranca_em
            ultima_dia = ultima.date() if hasattr(ultima, 'date') else ultima
            if ultima_dia == date.today():
                return False, 'Cobrança mensal já enviada hoje.'

        recipients = cls._destinatarios_cobranca(bolsista)
        if not recipients:
            return False, f'Sem e-mail do bolsista ou orientador para {bolsista.nome}.'

        subject, html, text_body = cls._build_message(bolsista, motivo)

        if dry_run:
            return True, f'[DRY-RUN] {motivo} → {", ".join(recipients)}'

        send_email(subject, recipients, html, text_body=text_body)
        bolsista.relatorio_ultima_cobranca_em = utc_now()
        cls._registrar_comentario_cobranca(bolsista, motivo, recipients, user_id=user_id)
        db.session.commit()

        log_action(
            'RELATORIO_FINAL_COBRANCA',
            tabela='bolsistas',
            registro_id=bolsista.id,
            detalhes=f"Motivo: {motivo}; Para: {', '.join(recipients)}",
        )
        return True, f'Cobrança ({motivo}) enviada para {", ".join(recipients)}.'

    @classmethod
    def enviar_na_desligamento(cls, bolsista, dry_run=False, user_id=None):
        if bolsista.relatorio_entregue:
            return False, None
        return cls.enviar_cobranca_individual(
            bolsista, motivo='desligamento', dry_run=dry_run, user_id=user_id
        )

    @classmethod
    def enviar_resumo_equipe(cls, pendentes, hoje=None, dry_run=False):
        hoje = hoje or date.today()
        if not pendentes:
            return False, None

        recipients = cls.get_equipe_recipients()
        if not recipients:
            return False, 'Configure o e-mail da equipe Robótica.'

        subject = (
            f'NAPI-Robótica — {len(pendentes)} relatório(s) final(is) pendente(s) — '
            f'{hoje.strftime("%d/%m/%Y")}'
        )
        html = render_template(
            'emails/cobranca_relatorio_final_resumo.html',
            pendentes=pendentes,
            data_ref=hoje,
            modelo_url=cls.modelo_url(),
        )
        linhas = []
        for b in pendentes:
            ref = cls.data_referencia_desligamento(b)
            linhas.append(
                f'- {b.nome} | Edital: {(b.edital.numero if b.edital else "-")} | '
                f'Desligamento: {ref.strftime("%d/%m/%Y") if ref else "-"} | '
                f'Bolsista: {b.email or "sem e-mail"} | Orientador: {b.email_orientador or "sem e-mail"}'
            )
        text_body = (
            f'Relatórios finais pendentes ({len(pendentes)}) em {hoje.strftime("%d/%m/%Y")}:\n\n'
            + '\n'.join(linhas)
            + f'\n\nModelo: {cls.modelo_url()}'
        )

        if dry_run:
            return True, f'[DRY-RUN] Resumo equipe → {", ".join(recipients)} ({len(pendentes)} pendente(s))'

        send_email(subject, recipients, html, text_body=text_body)
        log_action(
            'RELATORIO_FINAL_RESUMO_EQUIPE',
            tabela='bolsistas',
            registro_id=None,
            detalhes=f"Para: {', '.join(recipients)}; {len(pendentes)} pendente(s)",
        )
        return True, f'Resumo enviado para {", ".join(recipients)} ({len(pendentes)} pendente(s)).'

    @classmethod
    def processar_cobranca_dia_15(cls, dry_run=False, forcar=False):
        hoje = date.today()
        if not forcar and hoje.day != 15:
            return {
                'ok': True,
                'executado': False,
                'message': f'Hoje é dia {hoje.day}; cobrança mensal só no dia 15.',
            }

        pendentes = cls.listar_pendentes()
        if not pendentes:
            return {
                'ok': True,
                'executado': True,
                'enviados': 0,
                'message': 'Nenhum bolsista desligado com relatório pendente.',
            }

        enviados = 0
        erros = []
        detalhes = []

        for b in pendentes:
            try:
                ok, msg = cls.enviar_cobranca_individual(b, motivo='mensal', dry_run=dry_run)
                if ok:
                    enviados += 1
                    detalhes.append(f'{b.nome}: {msg}')
                else:
                    erros.append(f'{b.nome}: {msg}')
            except Exception as e:
                erros.append(f'{b.nome}: {e}')

        resumo_ok, resumo_msg = cls.enviar_resumo_equipe(pendentes, hoje=hoje, dry_run=dry_run)
        if resumo_ok and resumo_msg:
            detalhes.append(resumo_msg)

        return {
            'ok': len(erros) == 0,
            'executado': True,
            'total_pendentes': len(pendentes),
            'enviados': enviados,
            'erros': erros,
            'detalhes': detalhes,
            'message': (
                f'Cobrança dia 15: {enviados} e-mail(s) individuais, '
                f'{len(pendentes)} pendente(s), resumo equipe: '
                f'{"sim" if resumo_ok else "não"}.'
            ),
        }
