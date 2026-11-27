"""Cadastro novo (candidatura ainda sem bolsista) não pode esconder comentário nem abrir Ocorrências em branco."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORM = ROOT / 'templates' / 'bolsistas' / 'form.html'


def _form():
    return FORM.read_text(encoding='utf-8')


def test_aba_historico_de_comentarios_aparece_antes_de_salvar():
    texto = _form()
    abas = texto.split('class="tabs-container"', 1)[1].split('</div>', 1)[0]
    assert 'id="btn-tab-auditoria"' in abas
    assert 'Histórico e auditoria' in abas
    assert '{% if bolsista and bolsista.id %}' not in abas


def test_comentario_pode_ser_digitado_sem_bolsista_salvo():
    texto = _form()
    auditoria = texto.split('id="tab-auditoria"', 1)[1].split('END TAB HISTORICO E AUDITORIA', 1)[0]
    assert 'name="novo_comentario"' in auditoria
    assert 'if bolsista and bolsista.comentarios_historico' in auditoria
    assert 'Salvar' in auditoria


def test_ocorrencias_explica_que_so_depois_do_cadastro():
    texto = _form()
    historico = texto.split('id="tab-historico"', 1)[1].split('END TAB HISTORICO', 1)[0]
    assert 'id="ocorrencias-aguardando-cadastro"' in historico
    assert 'depois de salvar o cadastro' in historico
