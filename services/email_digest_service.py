"""E-mail resumo diario: tarefas da equipe + alertas operacionais (NAPI-Robotica)."""
import os
import sys
from datetime import date, timedelta
import calendar

from flask import render_template

from models import AnotacaoSistema, Edital, Bolsista
from utils.email_sender import send_email


def _console_safe(text):
    enc = getattr(sys.stdout, 'encoding', None) or 'utf-8'
    return text.encode(enc, errors='replace').decode(enc)


class EmailDigestService:
    @classmethod
    def build_tarefas_html(cls):
        pendentes = (
            AnotacaoSistema.query.filter_by(concluida=False)
            .order_by(AnotacaoSistema.criado_em.desc())
            .limit(30)
            .all()
        )
        if not pendentes:
            return '<p>Nenhuma tarefa pendente em /anotacoes/.</p>'
        items = ''.join(f'<li>{(t.texto or "")[:120]}</li>' for t in pendentes)
        return f'<p>Tarefas pendentes ({len(pendentes)}):</p><ul>{items}</ul>'

    @classmethod
    def build_alertas_html(cls):
        hoje = date.today()
        proximos_30 = hoje + timedelta(days=30)
        ultimo_dia = calendar.monthrange(hoje.year, hoje.month)[1]
        fim_mes = date(hoje.year, hoje.month, ultimo_dia)

        count_expiring = Edital.query.filter(
            Edital.data_fim >= hoje, Edital.data_fim <= proximos_30
        ).count()
        count_pending = Edital.query.filter(
            Edital.data_fim < hoje, Edital.prestacao_contas == False
        ).count()
        count_bolsistas = Bolsista.query.filter(
            Bolsista.data_fim_bolsa >= hoje,
            Bolsista.data_fim_bolsa <= fim_mes,
            Bolsista.ativo == True,
        ).count()
        count_titulacao = Bolsista.query.filter(
            Bolsista.ativo == True,
            Bolsista.previsao_defesa != None,
            Bolsista.previsao_defesa < hoje,
            Bolsista.data_fim_bolsa >= hoje,
        ).count()
        try:
            from services.ultimo_mes_bolsa_service import UltimoMesBolsaService
            count_ultimo_mes = UltimoMesBolsaService.contar_pendentes_aviso(hoje)
        except Exception:
            count_ultimo_mes = 0
        total = count_expiring + count_pending + count_bolsistas + count_titulacao + count_ultimo_mes

        if total == 0:
            return '<p>Nenhum alerta no painel Acoes Pendentes.</p>'

        return (
            '<p><strong>Alertas do sistema</strong></p><ul>'
            f'<li>Editais a vencer (30 dias): {count_expiring}</li>'
            f'<li>Prestacao de contas pendente: {count_pending}</li>'
            f'<li>Bolsas vencendo no mes: {count_bolsistas}</li>'
            f'<li>Titulacao antecipada: {count_titulacao}</li>'
            f'<li>Ultimo mes sem aviso enviado: {count_ultimo_mes}</li>'
            f'</ul><p>Total: <strong>{total}</strong></p>'
        )

    @classmethod
    def send_daily_digest(cls, dry_run=False):
        dest = os.getenv('NOTIFICATION_EMAIL') or os.getenv('MAIL_USERNAME')
        if not dest:
            return {'ok': False, 'message': 'NOTIFICATION_EMAIL nao configurado.'}

        hoje = date.today().strftime('%d/%m/%Y')
        corpo_html = (
            f'{cls.build_tarefas_html()}'
            f'<hr>{cls.build_alertas_html()}'
        )
        html = render_template(
            'emails/resumo_diario.html',
            data_ref=hoje,
            corpo_html=corpo_html,
        )
        subject = f'Arandu NAPI — resumo diario {hoje}'

        if dry_run:
            print(_console_safe(f'[DRY-RUN] Para: {dest}'))
            print(_console_safe(f'Assunto: {subject}'))
            print(_console_safe(html))
            return {
                'ok': True,
                'dry_run': True,
                'message': f'Simulacao: resumo para {dest}',
                'subject': subject,
                'to': dest,
            }

        send_email(subject=subject, recipients=[dest], html_body=html)
        return {'ok': True, 'to': dest, 'message': f'Resumo enviado para {dest}.'}
