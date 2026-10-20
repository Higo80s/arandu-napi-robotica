"""
Cobrança de Relatório Final — execução diária; envia no dia 15 de cada mês.

Desligamento imediato é disparado ao salvar cadastro (bolsistas.editar).
Teste: flask cobranca-relatorio-final --dry-run --forcar
"""
import click

from services.relatorio_final_service import RelatorioFinalService
from utils.task_notification import emit_task_notification


def init_app_tasks(app):
    @app.cli.command('cobranca-relatorio-final')
    @click.option('--dry-run', is_flag=True, help='Simula sem enviar e-mails')
    @click.option('--forcar', is_flag=True, help='Executa mesmo fora do dia 15')
    def cobranca_relatorio_final_command(dry_run, forcar):
        """Lembrete mensal (dia 15): bolsista + orientador + resumo equipe Robótica."""
        with app.app_context():
            result = RelatorioFinalService.processar_cobranca_dia_15(
                dry_run=dry_run, forcar=forcar
            )
            print(result.get('message', result))
            for linha in result.get('detalhes', []):
                print(f'  - {linha}'.encode('ascii', 'replace').decode('ascii'))
            for err in result.get('erros', []):
                print(f'  ! ERRO: {err}'.encode('ascii', 'replace').decode('ascii'))
            enviados = int(result.get('enviados') or 0)
            if enviados == 1:
                texto = 'Foi enviado um aviso por e-mail de cobrança de relatório final'
            elif enviados:
                texto = 'Foram enviados avisos por e-mail de cobrança de relatório final'
            else:
                texto = 'Nenhum aviso de cobrança de relatório final foi enviado hoje'
            emit_task_notification(texto, count=enviados)
            if not result.get('ok'):
                raise SystemExit(1)
