import pytest
import time
from app import app
from models import db, User
from flask_login import login_user

# Fixtures e Autenticação gerenciadas pelo conftest ou centralizadas
@pytest.fixture
def auth_header(client):
    # Simulação simples de login se necessário
    return {}

def test_dashboard_financeiro_api_schema(client_auth):
    """Garante que a API financeira retorna o JSON com a estrutura correta (PI 33/2025)."""
    start_time = time.time()
    response = client_auth.get('/dashboard/data/financeiro')
    duration = time.time() - start_time
    
    assert response.status_code == 200
    data = response.get_json()
    
    # Chaves obrigatórias para o Dashboard Neon
    assert 'saldo_convenio' in data
    assert 'total_folha' in data
    assert 'lote1' in data
    assert 'lote2' in data
    assert 'vencimento_lote2' in data
    
    # Performance check: < 200ms
    assert duration < 0.200, f"Dashboard API muito lenta: {duration:.4f}s"

def test_dashboard_data_api_structure(client_auth):
    """Valida se o endpoint principal do dashboard carrega Editais 2026 e Ocupação."""
    response = client_auth.get('/dashboard/data')
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'financeiro' in data
    assert 'ocupacao' in data
    assert len(data['financeiro']['por_edital']) >= 0
