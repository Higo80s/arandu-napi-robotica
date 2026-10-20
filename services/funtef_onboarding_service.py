"""Notificação FUNTEF após cadastro de novo bolsista (pré-requisito: Conveniar)."""
import os
import re

from flask import render_template

from audit import log_action
from core.datetime_utils import utc_now, format_datetime_br
from extensions import db
from models import SistemaConfig, ComentarioBolsista
from utils.email_sender import send_email

DEFAULT_FUNTEF_EMAILS = 'kamila.camelo@funtefpr.org.br'
DEFAULT_SECRETARIA_EMAIL = 'robotica-ct@utfpr.edu.br'
CONFIG_KEY_EMAILS = 'funtef_emails'
CONFIG_KEY_CORPO = 'funtef_email_corpo'
LOGO_STATIC = 'images/napi_robotica_logo.png'

DEFAULT_CORPO_EMAIL = """A secretaria do projeto NAPI-Robótica encaminha a documentação para cadastro de bolsista e informa que o(a) novo(a) bolsista já concluiu o cadastro na plataforma Conveniar.

Após verificação e elaboração do contrato da Fundação Araucária, por gentileza, enviar o documento para arquivo e confirmar a data de início do(a) bolsista no projeto para agendamento dos primeiros pagamentos.

Qualquer dúvida ou ajuste necessário, favor entrar em contato respondendo a este e-mail.

Atenciosamente,
Secretaria do Projeto NAPI-Robótica."""


def _get_config(chave):
    row = SistemaConfig.query.get(chave)
    return row.valor.strip() if row and row.valor else None


def _set_config(chave, valor):
    row = SistemaConfig.query.get(chave)
    if not row:
        db.session.add(SistemaConfig(chave=chave, valor=valor))
    else:
        row.valor = valor


class FuntefOnboardingService:
    @classmethod
    def logo_path(cls):
        from flask import current_app
        return os.path.join(current_app.static_folder, *LOGO_STATIC.split('/'))

    @classmethod
    def logo_url_preview(cls):
        """URL absoluta para prévia no admin (navegador)."""
        from flask import url_for, has_request_context
        if has_request_context():
            return url_for('static', filename=LOGO_STATIC, _external=True)
        base = (os.getenv('BASE_URL') or '').rstrip('/')
        return f'{base}/static/{LOGO_STATIC}' if base else ''

    @classmethod
    def get_secretaria_email(cls):
        """Cópia automática para a secretaria NAPI (não substitui destinatários FUNTEF)."""
        return (
            os.getenv('FUNTEF_COPIA_SECRETARIA')
            or os.getenv('NOTIFICATION_EMAIL')
            or os.getenv('MAIL_DEFAULT_SENDER', DEFAULT_SECRETARIA_EMAIL)
        ).strip()

    @classmethod
    def get_recipients_raw(cls):
        val = _get_config(CONFIG_KEY_EMAILS)
        if val:
            return val
        return os.getenv('FUNTEF_EMAILS', DEFAULT_FUNTEF_EMAILS).strip()

    @classmethod
    def get_funtef_external_recipients(cls):
        """E-mails externos FUNTEF (config/env/default). Exclui cópia secretaria."""
        secretaria = cls.get_secretaria_email().lower()
        raw = cls.get_recipients_raw()
        parts = re.split(r'[;,\n]+', raw) if raw else []
        emails = []
        for p in parts:
            p = p.strip()
            if p and '@' in p and p.lower() != secretaria:
                emails.append(p)
        if not emails:
            for p in re.split(r'[;,\s]+', DEFAULT_FUNTEF_EMAILS):
                p = p.strip()
                if p and '@' in p:
                    emails.append(p)
        elif not any('funtefpr' in e.lower() for e in emails):
            for p in re.split(r'[;,\s]+', DEFAULT_FUNTEF_EMAILS):
                p = p.strip()
                if p and '@' in p and p.lower() not in [e.lower() for e in emails]:
                    emails.append(p)
        seen = set()
        deduped = []
        for e in emails:
            key = e.lower()
            if key not in seen:
                seen.add(key)
                deduped.append(e)
        return deduped

    @classmethod
    def get_recipients(cls):
        """FUNTEF externa + cópia secretaria NAPI (sempre os dois lados)."""
        recipients = list(cls.get_funtef_external_recipients())
        secretaria = cls.get_secretaria_email()
        if secretaria and secretaria.lower() not in [e.lower() for e in recipients]:
            recipients.append(secretaria)
        return recipients

    @classmethod
    def get_email_body_raw(cls):
        val = _get_config(CONFIG_KEY_CORPO)
        return val if val else DEFAULT_CORPO_EMAIL

    @classmethod
    def email_body_to_html(cls, texto):
        """Converte parágrafos (linha em branco) em blocos HTML."""
        partes = [p.strip() for p in (texto or '').split('\n\n') if p.strip()]
        if not partes:
            partes = [DEFAULT_CORPO_EMAIL]
        return ''.join(f'<p style="margin:0 0 1rem;">{p.replace(chr(10), "<br>")}</p>' for p in partes)

    @classmethod
    def save_config(cls, emails_text, corpo_text):
        emails_text = (emails_text or '').strip()
        corpo_text = (corpo_text or '').strip()
        if not emails_text:
            return False, 'Informe ao menos um e-mail da FUNTEF.'
        if not corpo_text:
            return False, 'Informe o texto do e-mail.'
        secretaria = cls.get_secretaria_email().lower()
        recipients = [p.strip() for p in re.split(r'[;,\n]+', emails_text) if p.strip()]
        funtef_only = [r for r in recipients if '@' in r and r.lower() != secretaria]
        if not funtef_only:
            return False, (
                'Informe ao menos um e-mail da FUNTEF. '
                f'A cópia para {cls.get_secretaria_email()} é enviada automaticamente.'
            )
        _set_config(CONFIG_KEY_EMAILS, '; '.join(funtef_only))
        _set_config(CONFIG_KEY_CORPO, corpo_text)
        db.session.commit()
        return True, 'Configuração FUNTEF salva (destinatários e texto do e-mail).'

    @classmethod
    def save_recipients(cls, emails_text):
        return cls.save_config(emails_text, cls.get_email_body_raw())

    @classmethod
    def validate_stage_fields(cls, bolsista, conveniar_checked, link_pasta, contrato_pronto):
        """
        Valida transições do fluxo FUNTEF/Conveniar no formulário.
        Retorna lista de mensagens de erro (vazia = OK).
        """
        errors = []
        link = (link_pasta or '').strip()

        if conveniar_checked and not link:
            errors.append(
                'Informe o link da pasta na Nuvem antes de confirmar o cadastro no Conveniar.'
            )

        if contrato_pronto and not bolsista.funtef_email_enviado_em:
            errors.append(
                'Só marque o contrato como pronto após o e-mail FUNTEF ter sido enviado '
                '(Conveniar confirmado + link da Nuvem + salvar cadastro).'
            )

        return errors

    @classmethod
    def can_activate(cls, bolsista):
        """Pré-requisitos FUNTEF para ativar bolsista FA / governança NAPI."""
        if not bolsista.conveniar_cadastrado:
            return False, 'Ative somente após confirmar o cadastro no Conveniar.'
        if not (bolsista.link_pasta_nuvem or '').strip():
            return False, 'Informe o link da pasta na Nuvem antes de ativar o bolsista.'
        if not bolsista.funtef_email_enviado_em:
            return False, 'Ative somente após o envio do e-mail à FUNTEF.'
        if not bolsista.funtef_contrato_pronto:
            return False, 'Ative somente após marcar o contrato FUNTEF / Fundação Araucária como pronto.'
        return True, None

    @classmethod
    def _registrar_comentario(cls, bolsista, recipients, link, user_id=None, enviado_em=None, titulo='[E-MAIL FUNTEF]'):
        """Histórico de comentários: registro do e-mail FUNTEF enviado."""
        quando = format_datetime_br(enviado_em or utc_now())
        secretaria = cls.get_secretaria_email().lower()
        externos = [e for e in recipients if e.lower() != secretaria]
        copia = [e for e in recipients if e.lower() == secretaria]
        dest_externos = ', '.join(externos) if externos else '—'
        dest_copia = ', '.join(copia) if copia else '—'
        texto = (
            f'{titulo}\n'
            f'E-mail de verificação FUNTEF enviado em {quando}.\n'
            f'Destinatários FUNTEF: {dest_externos}\n'
            f'Cópia secretaria NAPI: {dest_copia}\n'
            f'Pasta na Nuvem: {link or "—"}'
        )
        bolsista.comentarios_historico.append(
            ComentarioBolsista(texto=texto, user_id=user_id)
        )

    @classmethod
    def _format_brl(cls, value):
        if value is None:
            return None
        try:
            n = float(value)
        except (TypeError, ValueError):
            return str(value)
        return f'R$ {n:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

    @classmethod
    def _email_context(cls, bolsista, link, corpo_html, logo_src):
        from utils import format_date_br

        edital = getattr(bolsista, 'edital', None)
        modalidade = getattr(bolsista, 'modalidade', None)
        edital_numero = edital.numero if edital else '-'
        valor = None
        if modalidade and getattr(modalidade, 'valor_mensal', None) is not None:
            valor = cls._format_brl(modalidade.valor_mensal)

        return {
            'bolsista': bolsista,
            'edital_numero': edital_numero,
            'numero_convenio': (getattr(edital, 'numero_convenio', None) or '').strip() or None,
            'coordenador_geral': (getattr(edital, 'coordenador_geral_proppg', None) or '').strip() or None,
            'modalidade': getattr(modalidade, 'nivel', None) if modalidade else None,
            'valor_parcela': valor,
            'qtd_parcelas': getattr(bolsista, 'meses_duracao', None),
            'data_nascimento': format_date_br(getattr(bolsista, 'data_nascimento', None)),
            'data_inicio': format_date_br(getattr(bolsista, 'data_inicio_bolsa', None)),
            'data_termino': format_date_br(getattr(bolsista, 'data_fim_bolsa', None)),
            'link_pasta': link,
            'corpo_html': corpo_html,
            'logo_src': logo_src,
        }

    @classmethod
    def _build_message(cls, bolsista, link, for_preview=False):
        edital = bolsista.edital if bolsista.edital else None
        edital_numero = edital.numero if edital else '-'
        subject = f'NAPI-Robótica — novo bolsista para verificação FUNTEF: {bolsista.nome}'
        corpo_texto = cls.get_email_body_raw()
        ctx = cls._email_context(
            bolsista,
            link,
            cls.email_body_to_html(corpo_texto),
            cls.logo_url_preview() if for_preview else 'cid:napi_logo',
        )
        html = render_template('emails/funtef_verificacao.html', **ctx)

        linhas = [
            corpo_texto,
            '',
            '--- Dados do projeto / edital ---',
            f'Edital: {edital_numero}',
        ]
        if ctx['numero_convenio']:
            linhas.append(f"Número do Convênio: {ctx['numero_convenio']}")
        if ctx['coordenador_geral']:
            linhas.append(f"Coordenador Geral / PROPPG: {ctx['coordenador_geral']}")
        if bolsista.processo_sei:
            linhas.append(f'Processo SEI: {bolsista.processo_sei}')
        linhas.extend([
            '',
            '--- Dados do novo bolsista / indicado ---',
            f'Nome Completo: {bolsista.nome}',
            f'CPF: {bolsista.cpf or "-"}',
        ])
        if ctx['data_nascimento']:
            linhas.append(f"Data de Nascimento: {ctx['data_nascimento']}")
        if bolsista.email:
            linhas.append(f'E-mail: {bolsista.email}')
        if getattr(bolsista, 'telefone', None):
            linhas.append(f'Telefone: {bolsista.telefone}')
        if ctx['modalidade']:
            linhas.append(f"Modalidade: {ctx['modalidade']}")
        if ctx['valor_parcela']:
            linhas.append(f"Valor da Parcela: {ctx['valor_parcela']}")
        if ctx['qtd_parcelas']:
            linhas.append(f"Quantidade de Parcelas: {ctx['qtd_parcelas']}")
        if ctx['data_inicio']:
            linhas.append(f"Início das Atividades: {ctx['data_inicio']}")
        if ctx['data_termino']:
            linhas.append(f"Término da Bolsa: {ctx['data_termino']}")
        linhas.extend(['', f'Pasta na Nuvem: {link}'])
        return subject, html, '\n'.join(linhas)

    @classmethod
    def render_preview_html(cls, corpo_text=None):
        """Prévia do e-mail com dados de exemplo (admin)."""
        from types import SimpleNamespace
        corpo = corpo_text if corpo_text is not None else cls.get_email_body_raw()
        sample_edital = SimpleNamespace(
            numero='03/2026',
            numero_convenio='CONV 110/2025',
            coordenador_geral_proppg='Nome Completo do Coordenador',
        )
        sample_mod = SimpleNamespace(nivel='Mestrado', valor_mensal=2100.00)
        sample = SimpleNamespace(
            nome='Nome do Bolsista (exemplo)',
            cpf='000.000.000-00',
            email='bolsista@exemplo.edu.br',
            telefone='(41) 99999-0000',
            data_nascimento=None,
            data_inicio_bolsa=None,
            data_fim_bolsa=None,
            meses_duracao=24,
            orientador='Orientador(a) Exemplo',
            processo_sei='SEI-0000/0000',
            edital=sample_edital,
            modalidade=sample_mod,
        )
        from datetime import date
        sample.data_nascimento = date(1998, 5, 15)
        sample.data_inicio_bolsa = date(2026, 4, 1)
        sample.data_fim_bolsa = date(2028, 3, 31)
        ctx = cls._email_context(
            sample,
            'https://nuvem.utfpr.edu.br/index.php/s/exemplo',
            cls.email_body_to_html(corpo),
            cls.logo_url_preview(),
        )
        # Preview: format dates via context helper (format_date_br on sample attrs)
        return render_template('emails/funtef_verificacao.html', **ctx)

    @classmethod
    def reenviar_funtef_externa(cls, bolsista, user_id=None, dry_run=False):
        """
        Reenvia só aos destinatários FUNTEF externos (ex.: config errada só com secretaria).
        Não altera funtef_email_enviado_em.
        """
        link = (bolsista.link_pasta_nuvem or '').strip()
        if not link:
            return False, 'Sem link da pasta na Nuvem.'
        externos = cls.get_funtef_external_recipients()
        if not externos:
            return False, 'Nenhum destinatário FUNTEF configurado.'
        subject, html, text_body = cls._build_message(bolsista, link)
        if dry_run:
            return True, f'[DRY-RUN] Reenvio FUNTEF → {", ".join(externos)}'
        send_email(subject, externos, html, text_body=text_body)
        cls._registrar_comentario(
            bolsista, externos, link, user_id=user_id,
            titulo='[E-MAIL FUNTEF — reenvio complementar]',
        )
        db.session.commit()
        log_action(
            'FUNTEF_EMAIL_RESEND',
            tabela='bolsistas',
            registro_id=bolsista.id,
            detalhes=f"Reenvio FUNTEF externa: {', '.join(externos)}; pasta: {link}",
        )
        return True, f'Reenviado para FUNTEF: {", ".join(externos)}.'

    @classmethod
    def try_send_notification(cls, bolsista, user_id=None):
        """
        Envia e-mail à FUNTEF se Conveniar confirmado + link da nuvem informado.
        Retorna (enviado: bool, mensagem: str|None).
        """
        if bolsista.funtef_email_enviado_em:
            return False, None

        if not bolsista.conveniar_cadastrado:
            return False, None

        link = (bolsista.link_pasta_nuvem or '').strip()
        if not link:
            return False, 'Informe o link da pasta na Nuvem para notificar a FUNTEF.'

        recipients = cls.get_recipients()
        if not cls.get_funtef_external_recipients():
            return False, 'Configure os e-mails da FUNTEF em Administração → E-mails FUNTEF.'

        link = (bolsista.link_pasta_nuvem or '').strip()
        subject, html, text_body = cls._build_message(bolsista, link)

        send_email(subject, recipients, html, text_body=text_body)

        bolsista.funtef_email_enviado_em = utc_now()
        cls._registrar_comentario(
            bolsista, recipients, link, user_id=user_id, enviado_em=bolsista.funtef_email_enviado_em
        )
        db.session.commit()

        externos = cls.get_funtef_external_recipients()
        secretaria = cls.get_secretaria_email()
        log_action(
            'FUNTEF_EMAIL_SENT',
            tabela='bolsistas',
            registro_id=bolsista.id,
            detalhes=(
                f"FUNTEF: {', '.join(externos)}; "
                f"Cópia: {secretaria}; pasta: {link}"
            ),
        )
        return True, (
            f'E-mail enviado para FUNTEF ({", ".join(externos)}) '
            f'e cópia ({secretaria}) em {format_datetime_br(bolsista.funtef_email_enviado_em)}.'
        )
