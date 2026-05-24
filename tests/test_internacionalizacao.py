import pytest
from app import app
from models import db, AcordoInternacional

@pytest.fixture
def client():
    # Agora o cliente vem do conftest.py ou configurado aqui se preferir isolar
    app.config['TESTING'] = True
    with app.app_context():
        # No Postgres nativo, dependemos do setup do conftest ou criamos aqui
        db.create_all()
        yield app.test_client()
        db.session.remove()
        # db.drop_all() # Evitar em Postgres compartilhado

def test_acordo_comum_sem_edital(client):
    """Teste: Acordo comum pode ser salvo sem edital."""
    with app.app_context():
        acordo = AcordoInternacional(
            pais="Argentina",
            instituicao="UBA",
            is_gcub=False
        )
        db.session.add(acordo)
        db.session.commit()
        assert acordo.id is not None
        assert acordo.numero_edital is None

def test_acordo_gcub_com_edital(client):
    """Teste: Acordo GCUB com edital deve ser salvo com sucesso."""
    with app.app_context():
        acordo = AcordoInternacional(
            pais="Colômbia",
            instituicao="UniAndes",
            is_gcub=True,
            numero_edital="EDITAL-01/2026"
        )
        db.session.add(acordo)
        db.session.commit()
        assert acordo.id is not None
        assert acordo.is_gcub is True

def test_acordo_gcub_sem_edital_falha(client):
    """Teste: Acordo GCUB sem edital deve lançar ValueError no commit."""
    with app.app_context():
        acordo = AcordoInternacional(
            pais="México",
            instituicao="UNAM",
            numero_edital=None,
            is_gcub=True
        )
        db.session.add(acordo)
        with pytest.raises(ValueError, match="O número do edital é obrigatório para acordos GCUB."):
             db.session.commit()
        db.session.rollback()

def test_normalizacao_edital(client):
    """Teste: Validação da normalização via formatter."""
    from utils.formatters import normalizar_edital
    entrada = " edital 005 / 2026 - proppg "
    esperado = "EDITAL-005/2026-PROPPG"
    assert normalizar_edital(entrada) == esperado
