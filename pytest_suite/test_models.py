import pytest
from models import Modalidade, Edital
from extensions import db

def test_modalidade_criacao_vagas(app):
    """Verifica se a capacidade de vagas e ocupacao funciona"""
    with app.app_context():
        novo_edital = Edital(numero='01/2026', agencia='CAPES')
        db.session.add(novo_edital)
        db.session.commit()

        mod = Modalidade(
            edital_id=novo_edital.id,
            nivel='Mestrado',
            vagas=5,
            valor_mensal=2100.0,
            max_meses=24
        )
        db.session.add(mod)
        db.session.commit()

        assert mod.vagas == 5
        assert len(mod.bolsistas) == 0

def test_vagas_placeholder(app):
    """Verifica comportamento provisório de Modalidade placeholder"""
    with app.app_context():
        mod = Modalidade(edital_id=1, nivel='Doutorado', vagas=999, valor_mensal=3100.0, max_meses=48)
        assert mod.vagas == 999
