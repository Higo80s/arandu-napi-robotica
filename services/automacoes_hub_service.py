"""Central de automações — catálogo operacional + último status em LogAutomacao.

Não gerencia o Windows Task Scheduler; apenas mostra o que existe, quando roda,
o último resultado e o link para configurar/disparar em cada página.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from models import LogAutomacao

CATALOG: list[dict[str, Any]] = [
    {
        'id': 'confirmacao_inicio',
        'nome': 'Confirmação de início de bolsa',
        'grupo': 'diario',
        'frequencia': 'Diário (rede de segurança)',
        'horario': '08:12',
        'tarefa_windows': 'AranduRobotica_ConfirmacaoInicioBolsa',
        'obs': 'Principal: Ativar Bolsista (Fundação) com prévia. Diário cobre ativos sem e-mail.',
        'log_names': ('Confirmação Início de Bolsa',),
        'config_endpoint': 'admin.config_confirmacao_inicio',
        'pendentes_fn': 'confirmacao_inicio',
    },
    {
        'id': 'ultimo_mes',
        'nome': 'Aviso último mês de bolsa',
        'grupo': 'diario',
        'frequencia': 'Diário',
        'horario': '08:10',
        'tarefa_windows': 'AranduRobotica_AvisoUltimoMesBolsa',
        'obs': '1× por bolsista/competência (mês de fim). Bolsista + orientador; resumo à equipe.',
        'log_names': ('Aviso Último Mês de Bolsa',),
        'config_endpoint': 'admin.config_ultimo_mes_bolsa',
        'pendentes_fn': 'ultimo_mes',
    },
    {
        'id': 'cobranca_relatorio',
        'nome': 'Cobrança relatório final',
        'grupo': 'diario',
        'frequencia': 'Diário (envio no dia 15)',
        'horario': '08:05',
        'tarefa_windows': 'AranduRobotica_CobrancaRelatorioFinal',
        'obs': 'Verifica todo dia; dispara de fato no dia 15 (ou forçar na tela).',
        'log_names': ('Cobrança Relatório Final',),
        'config_endpoint': 'admin.config_relatorio_final',
        'pendentes_fn': None,
    },
    {
        'id': 'resumo_diario',
        'nome': 'Resumo diário (tarefas + alertas)',
        'grupo': 'diario',
        'frequencia': 'Diário',
        'horario': '08:00',
        'tarefa_windows': 'AranduRobotica_ResumoDiario',
        'obs': 'Digest interno: anotações pendentes e alertas. Destinatário: NOTIFICATION_EMAIL.',
        'log_names': ('Resumo Diário', 'resumo_diario', 'Email Digest'),
        'config_endpoint': None,
        'pendentes_fn': None,
    },
    {
        'id': 'pagamento_bolsas',
        'nome': 'Pagamento de bolsas → Nuvem',
        'grupo': 'mensal',
        'frequencia': 'Mensal (dia 20)',
        'horario': '08:15',
        'tarefa_windows': 'AranduRobotica_PagamentoBolsasNuvem',
        'obs': (
            'Gera Excel, publica em /05_pagamentos e confirma por e-mail. '
            'Tarefa diária só executa no dia 20 (ou forçar na tela).'
        ),
        'log_names': ('Envio Pagamento de Bolsas (Nuvem)',),
        'config_endpoint': 'admin.config_pagamento_bolsas',
        'pendentes_fn': None,
    },
    {
        'id': 'funtef',
        'nome': 'FUNTEF onboarding',
        'grupo': 'sob_demanda',
        'frequencia': 'No cadastro / reenvio na ficha',
        'horario': '—',
        'tarefa_windows': None,
        'obs': 'E-mail à FUNTEF com link da pasta na Nuvem. 1× por bolsista (reenvio manual na ficha).',
        'log_names': ('FUNTEF Onboarding', 'FUNTEF', 'funtef_onboarding'),
        'config_endpoint': 'admin.config_funtef',
        'pendentes_fn': None,
    },
]

GRUPO_LABELS = {
    'diario': 'Diárias (verificação automática)',
    'mensal': 'Mensais',
    'sob_demanda': 'Sob demanda / manuais',
}


def _ultimo_log(nomes: tuple[str, ...]) -> LogAutomacao | None:
    if not nomes:
        return None
    return (
        LogAutomacao.query
        .filter(LogAutomacao.nome_tarefa.in_(nomes))
        .order_by(LogAutomacao.data_execucao.desc())
        .first()
    )


def _pendentes(key: str | None) -> int | None:
    if not key:
        return None
    try:
        if key == 'confirmacao_inicio':
            from services.confirmacao_inicio_bolsa_service import ConfirmacaoInicioBolsaService
            return len(ConfirmacaoInicioBolsaService.listar_elegiveis())
        if key == 'ultimo_mes':
            from services.ultimo_mes_bolsa_service import UltimoMesBolsaService
            if hasattr(UltimoMesBolsaService, 'contar_pendentes_aviso'):
                return UltimoMesBolsaService.contar_pendentes_aviso()
            if hasattr(UltimoMesBolsaService, 'listar_elegiveis'):
                return len(UltimoMesBolsaService.listar_elegiveis())
    except Exception:
        return None
    return None


def _smtp_configured() -> bool:
    import os
    user = (os.getenv('MAIL_USERNAME') or '').strip()
    return bool(user) and 'seu_email' not in user.lower()


def build_hub() -> dict[str, Any]:
    """Monta o contexto da Central de automações."""
    from flask import url_for

    itens = []
    alertas = 0
    for raw in CATALOG:
        log = _ultimo_log(tuple(raw['log_names']))
        pend = _pendentes(raw.get('pendentes_fn'))
        status = None
        when = None
        mensagem = None
        registros = None
        if log:
            status = (log.status or '').upper()
            when = log.data_execucao
            mensagem = (log.mensagem or '')[:220]
            registros = log.registros_processados
            if status in ('ERRO', 'PARCIAL'):
                alertas += 1

        config_url = None
        if raw.get('config_endpoint'):
            try:
                config_url = url_for(raw['config_endpoint'])
            except Exception:
                config_url = None

        itens.append({
            **{k: v for k, v in raw.items() if k != 'pendentes_fn'},
            'config_url': config_url,
            'ultimo_status': status,
            'ultimo_em': when,
            'ultimo_mensagem': mensagem,
            'ultimo_registros': registros,
            'pendentes': pend,
        })

    grupos: list[dict[str, Any]] = []
    for gid, glabel in GRUPO_LABELS.items():
        bloco = [i for i in itens if i['grupo'] == gid]
        if bloco:
            grupos.append({'id': gid, 'label': glabel, 'itens': bloco})

    recentes = (
        LogAutomacao.query
        .order_by(LogAutomacao.data_execucao.desc())
        .limit(12)
        .all()
    )

    return {
        'grupos': grupos,
        'alertas': alertas,
        'total': len(itens),
        'recentes': recentes,
        'agora': datetime.utcnow(),
        'smtp_configured': _smtp_configured(),
    }
