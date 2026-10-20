"""
Aviso do último mês de bolsa — execução diária (idempotente por competência).

Teste: flask aviso-ultimo-mes-bolsa --dry-run
"""
import click

from services.ultimo_mes_bolsa_service import UltimoMesBolsaService
from utils.task_notification import emit_task_notification


def init_app_tasks(app):
    @app.cli.command('aviso-ultimo-mes-bolsa')
    @click.option('--dry-run', is_flag=True, help='Simula sem enviar e-mails')
    @click.option('--forcar', is_flag=True, help='Reenvia mesmo se já notificado na competência')
    def aviso_ultimo_mes_bolsa_command(dry_run, forcar):
        """Notifica bolsista + orientador no último mês de vigência."""
        with app.app_context():
            result = UltimoMesBolsaService.processar_diario(
                dry_run=dry_run, forcar=forcar
            )
            print(result.get('message', result))
            for linha in result.get('detalhes', []):
                print(f'  - {linha}'.encode('ascii', 'replace').decode('ascii'))
            for err in result.get('erros', []):
                print(f'  ! ERRO: {err}'.encode('ascii', 'replace').decode('ascii'))
            enviados = int(result.get('enviados') or 0)
            if enviados == 1:
                texto = (
                    'Foi enviado um aviso por e-mail sobre o último mês '
                    'e a finalização de bolsa'
                )
            elif enviados:
                texto = (
                    'Foram enviados avisos por e-mail sobre o último mês '
                    'e a finalização de bolsas'
                )
            else:
                texto = (
                    'Nenhum aviso de último mês ou finalização de bolsa '
                    'foi enviado hoje'
                )
            emit_task_notification(texto, count=enviados)
            if not result.get('ok'):
                raise SystemExit(1)
