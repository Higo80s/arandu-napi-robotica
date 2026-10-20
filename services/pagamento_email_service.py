"""Configuração e disparo do e-mail de confirmação da folha de Pagamento de Bolsas."""
import os
import re
from datetime import date

from extensions import db
from models import SistemaConfig

CONFIG_KEY_CORPO = 'pagamento_bolsas_email_corpo'
CONFIG_KEY_EQUIPE = 'pagamento_bolsas_email_equipe'

MESES_PT = (
    'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
    'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro',
)

DEFAULT_CORPO = """Prezados,

A folha de Pagamento de Bolsas foi enviada com sucesso para a Nuvem NAPI-Robótica.

Competência: {competencia}
Vencimento: {vencimento}
Arquivo: {arquivo}
Pasta: /{pasta}/
Data do envio: {data_envio}

Este é um e-mail automático do sistema Arandú."""


def _get_config(chave):
    row = SistemaConfig.query.get(chave)
    return row.valor.strip() if row and row.valor else None


def _set_config(chave, valor):
    row = SistemaConfig.query.get(chave)
    if not row:
        db.session.add(SistemaConfig(chave=chave, valor=valor))
    else:
        row.valor = valor


class PagamentoEmailService:
    @classmethod
    def pasta_nuvem(cls):
        return os.getenv('CLOUD_PAGAMENTOS_FOLDER', '05_pagamentos').strip('/')

    @classmethod
    def get_email_body_raw(cls):
        return _get_config(CONFIG_KEY_CORPO) or DEFAULT_CORPO

    @classmethod
    def get_equipe_email_raw(cls):
        val = _get_config(CONFIG_KEY_EQUIPE)
        if val:
            return val
        return os.getenv(
            'PAGAMENTO_BOLSAS_EMAIL',
            os.getenv('NOTIFICATION_EMAIL', 'robotica-ct@utfpr.edu.br'),
        ).strip()

    @classmethod
    def get_recipients(cls):
        parts = re.split(r'[;,\s]+', cls.get_equipe_email_raw())
        return [p.strip() for p in parts if p.strip() and '@' in p]

    @classmethod
    def save_config(cls, corpo_text, equipe_emails):
        corpo_text = (corpo_text or '').strip()
        equipe_emails = (equipe_emails or '').strip()
        if not corpo_text:
            return False, 'Informe o texto do e-mail de confirmação.'
        if not equipe_emails:
            return False, 'Informe o e-mail da equipe (confirmação).'
        recipients = [p.strip() for p in re.split(r'[;,\n]+', equipe_emails) if p.strip()]
        if not any('@' in r for r in recipients):
            return False, 'E-mail da equipe inválido.'
        _set_config(CONFIG_KEY_CORPO, corpo_text)
        _set_config(CONFIG_KEY_EQUIPE, '; '.join(recipients))
        db.session.commit()
        return True, 'Configuração de pagamento de bolsas salva.'

    @classmethod
    def competencia_label(cls, mes_yyyy_mm):
        ano, mes = mes_yyyy_mm.split('-')
        return f'{MESES_PT[int(mes) - 1]}-{ano}'

    @classmethod
    def mes_vencimento(cls, mes_yyyy_mm):
        ano, mes = map(int, mes_yyyy_mm.split('-'))
        if mes == 12:
            return f'{MESES_PT[0]}-{ano + 1}'
        return f'{MESES_PT[mes]}-{ano}'

    @classmethod
    def nome_arquivo(cls, mes_yyyy_mm):
        return f'pagamento_{mes_yyyy_mm}.xlsx'

    @classmethod
    def default_mes(cls):
        return date.today().strftime('%Y-%m')

    @classmethod
    def fill_template(cls, corpo_text, mes_yyyy_mm, data_envio=None):
        data_envio = data_envio or date.today()
        replacements = {
            '{competencia}': cls.competencia_label(mes_yyyy_mm),
            '{vencimento}': cls.mes_vencimento(mes_yyyy_mm),
            '{arquivo}': cls.nome_arquivo(mes_yyyy_mm),
            '{pasta}': cls.pasta_nuvem(),
            '{data_envio}': data_envio.strftime('%d/%m/%Y'),
        }
        out = corpo_text or DEFAULT_CORPO
        for key, val in replacements.items():
            out = out.replace(key, val)
        return out

    @classmethod
    def build_subject(cls, mes_yyyy_mm):
        return f'Pagamento de Bolsas enviado — {cls.competencia_label(mes_yyyy_mm)}'

    @classmethod
    def render_preview_html(cls, mes_yyyy_mm=None, corpo_text=None):
        mes = mes_yyyy_mm or cls.default_mes()
        corpo = cls.fill_template(corpo_text if corpo_text is not None else cls.get_email_body_raw(), mes)
        paragraphs = []
        for block in corpo.split('\n\n'):
            block = block.strip()
            if not block:
                continue
            paragraphs.append(
                f'<p style="margin:0 0 1rem; white-space:pre-wrap;">{block}</p>'
            )
        recipients = cls.get_recipients()
        dest = ', '.join(recipients) if recipients else '—'
        html = f'''<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>Prévia</title></head>
<body style="font-family:Segoe UI,Arial,sans-serif;background:#f4f6f9;margin:0;padding:24px;">
<div style="max-width:640px;margin:0 auto;background:#fff;border-radius:8px;padding:28px;box-shadow:0 4px 6px rgba(0,0,0,.08);">
<p style="margin:0 0 1rem;color:#6b7280;font-size:13px;"><strong>Para:</strong> {dest}</p>
<p style="margin:0 0 1.25rem;font-size:15px;"><strong>Assunto:</strong> {cls.build_subject(mes)}</p>
<hr style="border:none;border-top:1px solid #e5e7eb;margin:0 0 1.25rem;">
{''.join(paragraphs)}
</div></body></html>'''
        return html, {
            'mes': mes,
            'competencia': cls.competencia_label(mes),
            'vencimento': cls.mes_vencimento(mes),
            'arquivo': cls.nome_arquivo(mes),
            'pasta': cls.pasta_nuvem(),
            'recipients': recipients,
            'subject': cls.build_subject(mes),
            'text_body': corpo,
        }

    @classmethod
    def disparar(cls, mes_yyyy_mm=None, forcar=True):
        """Gera Excel, sobe na Nuvem e envia confirmação (sempre forçado na UI)."""
        from flask import current_app
        from tasks.enviar_pagamento_bolsas import enviar_pagamento_bolsas

        mes = mes_yyyy_mm or cls.default_mes()
        app = current_app._get_current_object()
        resultado = enviar_pagamento_bolsas(app, mes_referencia=mes, forcar=forcar)
        if resultado is True:
            return True, f'Folha {cls.competencia_label(mes)} publicada na Nuvem e e-mail enviado.'
        if resultado == 'ja_enviado':
            return True, f'Folha {cls.competencia_label(mes)} já estava na Nuvem hoje.'
        if resultado is None:
            return False, 'Envio não executado (fora do dia 20). Use forçar.'
        return False, 'Falha no envio. Veja o Monitor de Automação para detalhes.'
