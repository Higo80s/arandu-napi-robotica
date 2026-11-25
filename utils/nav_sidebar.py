"""Item ativo do menu lateral. Mesma ideia do PROPPG, só com as rotas da NAPI."""

from __future__ import annotations

from collections.abc import Callable

NavMatcher = Callable[[str, str], bool]

# Ordem importa: regras mais específicas primeiro.
NAV_RULES: list[tuple[str, NavMatcher]] = [
    ('dashboard', lambda ep, _: ep in (
        'index', 'dashboard.master', 'dashboard.coordenacao', 'dashboard.direcao',
    )),
    ('diversidade', lambda ep, p: (
        ep == 'bolsistas.diversidade'
        or p.startswith('/diversidade')
        or p.startswith('/bolsistas/diversidade')
    )),
    ('alertas', lambda ep, _: ep in (
        'dashboard.alertas', 'dashboard.exportar_pendencias_excel',
    )),
    ('analytics', lambda ep, _: ep == 'dashboard.advanced'),
    ('programas', lambda ep, _: bool(ep) and ep.startswith('admin.admin_programas')),
    ('emails_pagamento', lambda ep, _: bool(ep) and 'pagamento_bolsas' in ep),
    ('emails_inicio', lambda ep, _: bool(ep) and 'confirmacao_inicio' in ep),
    ('emails_funtef', lambda ep, _: bool(ep) and ep.startswith('admin.') and 'funtef' in ep),
    ('emails_relatorio', lambda ep, _: bool(ep) and 'relatorio_final' in ep),
    ('emails_ultimo_mes', lambda ep, _: bool(ep) and 'ultimo_mes' in ep),
    ('automacoes_hub', lambda ep, _: ep in ('admin.automacoes_hub', 'admin.monitor_automacao')),
    ('consolidado', lambda ep, _: ep in ('admin.admin_consolidado', 'admin.download_consolidado')),
    ('manual', lambda ep, _: ep in ('admin.manual', 'admin.documentacao', 'admin.sobre_simbolo')),
    ('admin_users', lambda ep, _: bool(ep) and ep.startswith('admin_users.')),
    ('editais', lambda ep, _: bool(ep) and ep.startswith('editais.')),
    ('bolsistas', lambda ep, _: bool(ep) and ep.startswith('bolsistas.')),
    ('reports', lambda ep, _: bool(ep) and (ep.startswith('reports.') or ep.startswith('reports_bp.'))),
    ('anotacoes', lambda ep, _: bool(ep) and ep.startswith('anotacoes.')),
]


def resolve_active_nav(endpoint: str | None, path: str = '') -> str | None:
    ep = endpoint or ''
    p = path or ''
    for key, matcher in NAV_RULES:
        if matcher(ep, p):
            return key
    return None
