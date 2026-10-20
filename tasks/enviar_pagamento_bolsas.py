"""
Envio automático da folha Pagamento de Bolsas (Excel) para a Nuvem UTFPR.

Agendamento: dia 20 de cada mês (competência do mês corrente).
Teste/manual: flask enviar-pagamento-bolsas --mes 2026-05 --forcar
"""
from datetime import date, datetime

import click
from flask_mail import Message

from core.datetime_utils import BR_TZ, UTC
from extensions import db, mail
from models import LogAutomacao
from reports import gerar_relatorio_excel
from services.nuvem_service import upload_bytes
from services.pagamento_email_service import PagamentoEmailService
from utils.task_notification import emit_task_notification

LOG_NOME = 'Envio Pagamento de Bolsas (Nuvem)'


def _inicio_hoje_utc_naive():
    inicio_br = datetime.now(BR_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    return inicio_br.astimezone(UTC).replace(tzinfo=None)


def _pagamento_ja_enviado_hoje(filename):
    return (
        LogAutomacao.query
        .filter(LogAutomacao.nome_tarefa == LOG_NOME)
        .filter(LogAutomacao.status == 'SUCESSO')
        .filter(LogAutomacao.data_execucao >= _inicio_hoje_utc_naive())
        .filter(LogAutomacao.mensagem.ilike(f'%{filename}%'))
        .first()
    ) is not None


def enviar_pagamento_bolsas(app, mes_referencia=None, forcar=False):
    """
    Gera Excel, envia para Nuvem /05_pagamentos e confirma por e-mail.
    Sem --forcar, só executa no dia 20 (competência = mês corrente).
    """
    hoje = date.today()
    if mes_referencia is None:
        mes_referencia = hoje.strftime('%Y-%m')

    if not forcar and hoje.day != 20:
        print(f"[PAGAMENTO] Hoje ({hoje:%d/%m/%Y}) não é dia 20. Use --forcar para envio manual.")
        return None

    svc = PagamentoEmailService
    filename = svc.nome_arquivo(mes_referencia)
    if not forcar and _pagamento_ja_enviado_hoje(filename):
        print(f'[PAGAMENTO] Já enviado hoje: {filename}. Ignorando duplicata.')
        return 'ja_enviado'

    log = LogAutomacao(nome_tarefa=LOG_NOME)
    comp_label = svc.competencia_label(mes_referencia)
    pasta = svc.pasta_nuvem()
    remote_path = f'{pasta}/{filename}'
    recipients = svc.get_recipients()

    try:
        if not recipients:
            raise RuntimeError('Nenhum destinatário configurado para confirmação de pagamento.')

        excel_buffer = gerar_relatorio_excel(mes_referencia)
        file_bytes = excel_buffer.getvalue()
        if not file_bytes:
            raise RuntimeError('Relatório Excel gerado vazio.')

        upload_bytes(
            remote_path,
            file_bytes,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

        corpo = svc.fill_template(svc.get_email_body_raw(), mes_referencia, data_envio=hoje)
        msg = Message(
            subject=f'✅ {svc.build_subject(mes_referencia)}',
            recipients=recipients,
            body=corpo,
        )
        mail.send(msg)

        log.status = 'SUCESSO'
        log.mensagem = (
            f'Arquivo {filename} enviado para /{pasta}/. '
            f'E-mail: {", ".join(recipients)}'
        )
        log.registros_processados = len(file_bytes)
        print(f'[PAGAMENTO] Enviado: {remote_path} ({len(file_bytes)} bytes)')
        return True

    except Exception as e:
        log.status = 'ERRO'
        log.mensagem = str(e)
        log.registros_processados = 0
        print(f'[PAGAMENTO] ERRO: {e}')
        try:
            if recipients:
                err_msg = Message(
                    subject=f'⚠️ Falha no envio Pagamento de Bolsas — {comp_label}',
                    recipients=recipients,
                    body=f'Falha ao enviar a folha de competência {comp_label}:\n\n{e}\n',
                )
                mail.send(err_msg)
        except Exception:
            pass
        return False

    finally:
        db.session.add(log)
        db.session.commit()


def init_app_tasks(app):
    @app.cli.command('enviar-pagamento-bolsas')
    @click.option('--mes', default=None, help='Competência YYYY-MM (ex: 2026-05)')
    @click.option('--forcar', is_flag=True, help='Executa mesmo fora do dia 20')
    def enviar_pagamento_bolsas_command(mes, forcar):
        """Envia folha Pagamento de Bolsas para a Nuvem e confirma por e-mail."""
        with app.app_context():
            resultado = enviar_pagamento_bolsas(
                app, mes_referencia=mes, forcar=forcar
            )
            dest = ', '.join(PagamentoEmailService.get_recipients())
            if resultado is True:
                emit_task_notification(
                    'Foi enviada a confirmação da folha de pagamento publicada na Nuvem',
                    count=1,
                    recipients=dest,
                )
            elif resultado == 'ja_enviado':
                emit_task_notification(
                    'A folha de pagamento já estava publicada na Nuvem',
                    count=0,
                )
            elif resultado is None:
                emit_task_notification(
                    'Nenhuma folha de pagamento estava programada para hoje',
                    count=0,
                )
            else:
                emit_task_notification(
                    'Nenhuma confirmação de folha de pagamento foi enviada',
                    count=0,
                )
                raise SystemExit(1)
