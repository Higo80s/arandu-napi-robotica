"""
Envio automático da folha Pagamento de Bolsas (Excel) para a Nuvem UTFPR.

Agendamento: diário (Task Scheduler). A folha só sai a partir do dia 20 do
mês de referência; se esse dia for perdido, a primeira execução posterior
publica o atrasado (idempotente via LogAutomacao) — mesmo padrão PROPPG.

Teste/manual: flask enviar-pagamento-bolsas --mes 2026-05 --forcar
"""
from datetime import date, datetime
from typing import Callable, Optional

import click
from dateutil.relativedelta import relativedelta
from flask_mail import Message

from core.datetime_utils import BR_TZ, UTC
from extensions import db, mail
from models import LogAutomacao
from reports import gerar_relatorio_excel
from services.nuvem_service import upload_bytes
from services.pagamento_email_service import PagamentoEmailService
from utils.task_notification import emit_task_notification

LOG_NOME = 'Envio Pagamento de Bolsas (Nuvem)'
DIA_PUBLICACAO_FOLHA = 20


def _inicio_hoje_utc_naive():
    inicio_br = datetime.now(BR_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    return inicio_br.astimezone(UTC).replace(tzinfo=None)


def _folha_ja_publicada(mes_yyyy_mm: str) -> bool:
    """True se já existe SUCESSO para pagamento_YYYY-MM.xlsx."""
    filename = PagamentoEmailService.nome_arquivo(mes_yyyy_mm)
    return (
        LogAutomacao.query
        .filter(LogAutomacao.nome_tarefa == LOG_NOME)
        .filter(LogAutomacao.status == 'SUCESSO')
        .filter(LogAutomacao.mensagem.ilike(f'%{filename}%'))
        .first()
    ) is not None


def ultimo_mes_folha_devido(hoje: Optional[date] = None) -> date:
    """Último mês de referência cuja data de publicação (dia 20) já passou."""
    hoje = hoje or date.today()
    mes_atual = date(hoje.year, hoje.month, 1)
    if hoje.day >= DIA_PUBLICACAO_FOLHA:
        return mes_atual
    return mes_atual - relativedelta(months=1)


def mes_folha_pendente(
    hoje: Optional[date] = None,
    ja_enviado: Optional[Callable[[date], bool]] = None,
) -> Optional[date]:
    """Mais antigo mês devido ainda sem publicação SUCESSO.

    Janela: mês devido atual + mês anterior (catch-up se o dia 20 foi perdido).
    """
    hoje = hoje or date.today()
    devido = ultimo_mes_folha_devido(hoje)
    candidatos = [devido - relativedelta(months=1), devido]

    def _default_ja_enviado(mes: date) -> bool:
        return _folha_ja_publicada(mes.strftime('%Y-%m'))

    check = ja_enviado or _default_ja_enviado
    for mes in candidatos:
        dia_limite = date(mes.year, mes.month, DIA_PUBLICACAO_FOLHA)
        if hoje < dia_limite:
            continue
        if not check(mes):
            return mes
    return None


def _executar_envio(app, mes_referencia, forcar=False):
    """Gera Excel, sobe para a Nuvem e confirma por e-mail. Grava LogAutomacao."""
    hoje = date.today()
    svc = PagamentoEmailService
    filename = svc.nome_arquivo(mes_referencia)

    if not forcar and _folha_ja_publicada(mes_referencia):
        print(f'[PAGAMENTO] Já publicado: {filename}. Ignorando duplicata.')
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


def enviar_pagamento_bolsas(app, mes_referencia=None, forcar=False):
    """
    Publica folha na Nuvem /05_pagamentos e confirma por e-mail.

    Sem --forcar: resolve competência pendente (dia 20+ ou catch-up).
    Com --forcar: usa --mes ou mês corrente e republica.
    """
    hoje = date.today()

    if forcar:
        if mes_referencia is None:
            mes_referencia = hoje.strftime('%Y-%m')
        print(f'[PAGAMENTO][FORCAR] Republicando competência {mes_referencia}')
        return _executar_envio(app, mes_referencia, forcar=True)

    if mes_referencia:
        # Chamada explícita com mês, sem forçar: só envia se devido e ainda não publicado
        ano, mes = map(int, mes_referencia.split('-'))
        dia_limite = date(ano, mes, DIA_PUBLICACAO_FOLHA)
        if hoje < dia_limite:
            print(
                f'[PAGAMENTO] Competência {mes_referencia} só a partir de '
                f'{dia_limite:%d/%m/%Y}.'
            )
            return None
        return _executar_envio(app, mes_referencia, forcar=False)

    pendente = mes_folha_pendente(hoje)
    if pendente is None:
        print(
            '[PAGAMENTO] Nenhuma folha pendente '
            '(antes do dia 20 ou competência já publicada).'
        )
        return None

    mes_referencia = pendente.strftime('%Y-%m')
    if pendente.month != hoje.month or pendente.year != hoje.year:
        print(
            f'[PAGAMENTO][CATCH-UP] Folha atrasada: {mes_referencia} '
            f'(publicação devida desde o dia {DIA_PUBLICACAO_FOLHA}).'
        )
    return _executar_envio(app, mes_referencia, forcar=False)


def init_app_tasks(app):
    @app.cli.command('enviar-pagamento-bolsas')
    @click.option('--mes', default=None, help='Competência YYYY-MM (ex: 2026-05)')
    @click.option('--forcar', is_flag=True, help='Republica ignorando LogAutomacao')
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
