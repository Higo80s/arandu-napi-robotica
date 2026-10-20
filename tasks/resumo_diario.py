"""CLI: resumo diario por e-mail (tarefas + alertas)."""
import click

from services.email_digest_service import EmailDigestService
from utils.task_notification import emit_task_notification


def init_app_tasks(app):
    @app.cli.command('send-daily-digest')
    @click.option('--dry-run', is_flag=True, help='Simula sem enviar e-mail')
    def send_daily_digest_command(dry_run):
        """Envia resumo diario: tarefas pendentes + alertas do sistema."""
        with app.app_context():
            result = EmailDigestService.send_daily_digest(dry_run=dry_run)
            print(result.get('message', result))
            enviado = 1 if result.get('ok') and not dry_run else 0
            texto = (
                'Foi enviado o resumo diário de tarefas e alertas por e-mail'
                if enviado
                else 'Nenhum resumo diário de tarefas e alertas foi enviado hoje'
            )
            emit_task_notification(
                texto,
                count=enviado,
                recipients=result.get('to'),
            )
            if not result.get('ok'):
                raise SystemExit(1)
