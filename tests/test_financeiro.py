import pytest
from app import app
from models import db, Acompanhamento, Bolsista, Modalidade
from services.financeiro_service import FinanceiroService
from datetime import date

# Fixtures (app, db, client) são providas pelo conftest.py

def test_saldo_projeto_calculo(client):
    """Valida se o saldo do projeto (R$ 5.9M) diminui corretamente com pagamentos."""
    with app.app_context():
        # Setup: Criar um bolsista e um pagamento
        # Importante: FinanceiroService usa 'valor_mensal' e 'nivel'
        mod = Modalidade(nome="Mestrado", valor_mensal=2100.0, nivel="mestrado")
        db.session.add(mod)
        db.session.commit()

        # Importante: FinanceiroService filtra por ativo=True
        bolsista = Bolsista(nome="Bolsista Teste", modalidade_id=mod.id, ativo=True)
        db.session.add(bolsista)
        db.session.commit()

        # Adicionar 2 pagamentos
        p1 = Acompanhamento(bolsista_id=bolsista.id, status_pagamento="Pago", valor_pago=2100.0, mes_referencia=1, ano_referencia=2024)
        p2 = Acompanhamento(bolsista_id=bolsista.id, status_pagamento="Pago", valor_pago=2100.0, mes_referencia=2, ano_referencia=2024)
        db.session.add_all([p1, p2])
        db.session.commit()

        metrics = FinanceiroService.get_project_metrics() # Nome correto
        
        # Teto: 5.910.124,50 - (2100 * 2) = 5.905.924,50
        expected_saldo = 5910124.50 - 4200.0
        assert metrics['saldo_convenio'] == expected_saldo
        assert metrics['total_folha'] == 2100.0 

def test_segregacao_lotes(client):
    """Valida se o sistema separa corretamente Lote 30 de Lote 5º DU."""
    with app.app_context():
        # Lote 30 (Pesquisador -> Categoria Pesquisador)
        m1 = Modalidade(nome="Pesquisador A", valor_mensal=3000.0, nivel="pesquisador")
        # Lote 5º DU (Graduação -> Categoria IC)
        m2 = Modalidade(nome="Iniciação Científica", valor_mensal=700.0, nivel="iniciacao cientifica")
        db.session.add_all([m1, m2])
        db.session.commit()

        b1 = Bolsista(nome="Mestre", modalidade_id=m1.id, ativo=True)
        b2 = Bolsista(nome="Estudante", modalidade_id=m2.id, ativo=True)
        db.session.add_all([b1, b2])
        db.session.commit()

        metrics = FinanceiroService.get_project_metrics()
        
        assert metrics['lote30'] == 3000.0
        assert metrics['lote5du'] == 700.0
        assert metrics['total_folha'] == 3700.0
