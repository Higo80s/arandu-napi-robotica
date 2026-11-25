"""NAPI não expõe módulos herdados da PROPPG (PROAP, CAPES, inter, pós-doc, explorer)."""
from pathlib import Path

from utils.nav_sidebar import resolve_active_nav

ROOT = Path(__file__).resolve().parents[2]

FORA_DO_MENU = (
    'proap.',
    'dashboard.capes',
    'inter.index',
    'database_explorer.',
    'ui_editor.',
    'posdoc.',
)


def _texto(*relativos):
    return '\n'.join(
        (ROOT / rel).read_text(encoding='utf-8') for rel in relativos
    )


def test_menu_nao_aponta_modulos_fora_do_escopo():
    telas = _texto(
        'templates/base.html',
        'templates/dashboard/coordinator.html',
        'templates/dashboard/modern.html',
        'templates/bolsistas/form.html',
        'templates/bolsistas/importar.html',
        'templates/editais/form.html',
        'app.py',
    )
    for trecho in FORA_DO_MENU:
        assert trecho not in telas, trecho


def test_edital_nao_vincula_proap():
    texto = (ROOT / 'services' / 'edital_service.py').read_text(encoding='utf-8')
    assert 'proap_distribuicao_id' not in texto


def test_promocao_nao_desvia_para_posdoc():
    editais = (ROOT / 'blueprints' / 'editais.py').read_text(encoding='utf-8')
    bolsistas = (ROOT / 'blueprints' / 'bolsistas.py').read_text(encoding='utf-8')
    assert 'posdoc' not in editais.lower()
    assert 'mobilidade_novo' not in bolsistas
    assert 'posdoc_index' not in bolsistas


def test_menu_ativo_segue_a_rota_como_no_modelo():
    assert resolve_active_nav('index', '/') == 'dashboard'
    assert resolve_active_nav('editais.index', '/editais') == 'editais'
    assert resolve_active_nav('bolsistas.diversidade', '/diversidade') == 'diversidade'
    assert resolve_active_nav('admin.config_funtef', '/admin/config-funtef') == 'emails_funtef'
    assert resolve_active_nav('admin.automacoes_hub', '/admin/automacoes') == 'automacoes_hub'
    assert resolve_active_nav('bolsistas.editar', '/bolsistas/1/editar') == 'bolsistas'
