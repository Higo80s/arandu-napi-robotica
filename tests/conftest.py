import pytest
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente ANTES de importar o app (exigência v10.7)
load_dotenv()

from app import app as flask_app
from extensions import db as _db

@pytest.fixture(scope='session')
def app():
    """Session-wide test `Flask` application."""
    # Garante que o DATABASE_URL de teste seja usado se presente, senão usa o do .env (CUIDADO!)
    test_db = os.getenv('TEST_DATABASE_URL')
    if test_db:
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = test_db
    
    flask_app.config['TESTING'] = True
    
    with flask_app.app_context():
        yield flask_app

@pytest.fixture(scope='session')
def db(app):
    """Session-wide test database."""
    # No Postgres, geralmente não queremos dar drop_all se for a base real.
    # Mas para CI/CD ou bases de teste isoladas, é o padrão.
    _db.create_all()
    yield _db
    _db.session.remove()
    # _db.drop_all() # Opcional: manter para depuração se necessário

@pytest.fixture(scope='function')
def session(db):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    # Criar uma sessão vinculada à conexão/transação
    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)
    
    db.session = session
    
    yield session
    
    transaction.rollback()
    connection.close()
    session.remove()

@pytest.fixture(scope='function')
def client(app):
    """A Flask test client."""
    return app.test_client()
