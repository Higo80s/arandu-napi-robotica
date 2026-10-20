"""
Confirmação de início de bolsa — rede de segurança diária.

Disparo principal: tela do bolsista (Ativar com prévia, ou reenvio manual).
Teste: flask confirmacao-inicio-bolsa --dry-run
"""
import click

from services.confirmacao_inicio_bolsa_service import ConfirmacaoInicioBolsaService
from utils.task_notification import emit_task_notification


def init_app_tasks(app):
    @app.cli.command('confirmacao-inicio-bolsa')
    @click.option('--dry-run', is_flag=True, help='Simula sem enviar e-mails')
    @click.option('--forcar', is_flag=True, help='Reenvia mesmo se já notificado')
    def confirmacao_inicio_bolsa_command(dry_run, forcar):
        """Notifica ativos implantados ainda sem confirmação de início."""
        with app.app_context():
            result = ConfirmacaoInicioBolsaService.processar_diario(
                dry_run=dry_run, forcar=forcar
            )
            print(result.get('message', result))
            for linha in result.get('detalhes', []):
                print(f'  - {linha}'.encode('ascii', 'replace').decode('ascii'))
            for err in result.get('erros', []):
                print(f'  ! ERRO: {err}'.encode('ascii', 'replace').decode('ascii'))
            enviados = int(result.get('enviados') or 0)
            if enviados == 1:
                texto = 'Foi enviado um e-mail de confirmação de início de bolsa'
            elif enviados:
                texto = 'Foram enviados e-mails de confirmação de início de bolsa'
            else:
                texto = 'Nenhuma confirmação de início de bolsa foi enviada hoje'
            emit_task_notification(texto, count=enviados)
            if not result.get('ok'):
                raise SystemExit(1)
