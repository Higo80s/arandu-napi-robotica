import pytest

def test_login_page_loads(client):
    """Verifica se a página de login carrega o HTML corretamente"""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b"Entrar" in response.data or b"Login" in response.data

def test_dashboard_redireciona_deslogado(client):
    """Verifica se rota protegida barra visitantes nÃ£o autenticados"""
    response = client.get('/')
    assert response.status_code == 302
    assert '/auth/login' in response.headers.get('Location', '')
def test_dashboard_acesso_logado(auth_client):
    """Verifica se o master autenticado acessa o painel"""
    response = auth_client.get('/')
    assert response.status_code == 200
    assert b"Sair" in response.data

def test_rota_bolsistas(auth_client):
    """Verifica a listagem geral do index de bolsistas"""
    response = auth_client.get('/bolsistas')
    assert response.status_code == 200

