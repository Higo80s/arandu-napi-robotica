import os
import pytest
from sqlalchemy import text
from app import app as flask_app
from extensions import db, migrate
from models import User

@pytest.fixture(scope="session")
def app():
    # Setup App para testes
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "postgresql://postgres:admin123@localhost:5432/gestao_editais_test",
        "WTF_CSRF_ENABLED": False,
        "LOGIN_DISABLED": False,
    })
    
    with flask_app.app_context():
        # Drop tudo para garantir recomeço limpo e cria schema nativo 
        db.session.execute(text('DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO postgres; GRANT ALL ON SCHEMA public TO public;'))
        db.session.commit()
        db.create_all()
        
        # Inserir dados básicos para testes
        try:
            admin_user = User(
                username='admin_teste', 
                email='admin@teste.com',
                origem='local',
                role='master',
                must_change_password=False
            )
            admin_user.set_password('teste123')
            db.session.add(admin_user)
            db.session.commit()
        except Exception as e:
            import traceback
            traceback.print_exc()

        yield flask_app
        
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

@pytest.fixture()
def auth_client(client, app):
    # Loga o admin_teste no client
    resp = client.post('/auth/login', data={
        'email': 'admin@teste.com',
        'password': 'teste123'
    }, follow_redirects=True)
    
    assert b'Email ou senha incorretos' not in resp.data
    return client
