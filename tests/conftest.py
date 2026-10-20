"""Pytest: tests/unit não usa banco; o restante exige TEST_DATABASE_URL isolada."""
import os
from pathlib import Path
from urllib.parse import urlparse

import pytest
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

collect_ignore_glob = ['quotas_lab/*']
UNIT_ROOT = Path(__file__).resolve().parent / 'unit'


def _db_identity(url):
    u = urlparse(url)
    return ((u.hostname or '').lower(), u.port or 5432, (u.path or '').lstrip('/'))


def _isolated_test_url():
    test_url = (os.getenv('TEST_DATABASE_URL') or '').strip()
    if not test_url:
        return None
    prod_url = (os.getenv('DATABASE_URL') or '').strip()
    if prod_url and _db_identity(test_url) == _db_identity(prod_url):
        pytest.exit('TEST_DATABASE_URL aponta para o mesmo banco de DATABASE_URL. Abortado.', returncode=2)
    if 'test' not in _db_identity(test_url)[2].lower():
        pytest.exit('O nome do banco de TEST_DATABASE_URL deve conter "test".', returncode=2)
    return test_url


TEST_DATABASE_URL = _isolated_test_url()


def pytest_ignore_collect(collection_path, config):
    path = Path(str(collection_path)).resolve()
    if path == UNIT_ROOT or UNIT_ROOT in path.parents:
        return False
    if TEST_DATABASE_URL:
        return None
    if path.suffix == '.py':
        return True
    return None


def pytest_report_header(config):
    if TEST_DATABASE_URL:
        return ['Banco de teste isolado: TEST_DATABASE_URL']
    return ['TEST_DATABASE_URL ausente: só tests/unit (sem Postgres/produção).']


def _neutralize_external_services():
    for name in list(os.environ):
        if name.startswith(('MAIL_', 'CLOUD_')) or name.endswith('_EMAIL') or name.endswith('_EMAILS'):
            os.environ[name] = ''
    os.environ['MAIL_SERVER'] = 'localhost'
    os.environ['MAIL_PORT'] = '1'


if TEST_DATABASE_URL:
    _neutralize_external_services()
    os.environ['DATABASE_URL'] = TEST_DATABASE_URL
    from app import app as flask_app  # noqa: E402
    from extensions import db as _db  # noqa: E402
    from sqlalchemy import text  # noqa: E402

    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    flask_app.config['MAIL_SUPPRESS_SEND'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DATABASE_URL

    @pytest.fixture(scope='session')
    def app():
        yield flask_app

    @pytest.fixture(scope='session')
    def db(app):
        with app.app_context():
            engine_db = _db.engine.url.database or ''
            if engine_db != _db_identity(TEST_DATABASE_URL)[2]:
                pytest.exit(
                    f'Engine conectado a "{engine_db}", não ao banco de teste. Abortado.',
                    returncode=2,
                )
            _db.session.execute(text('DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;'))
            _db.session.commit()
            _db.create_all()
            yield _db
            _db.session.remove()

    @pytest.fixture(scope='function')
    def session(db):
        connection = db.engine.connect()
        transaction = connection.begin()
        options = dict(bind=connection, binds={})
        scoped = db.create_scoped_session(options=options)
        db.session = scoped
        yield scoped
        transaction.rollback()
        connection.close()
        scoped.remove()

    @pytest.fixture(scope='function')
    def client(app):
        return app.test_client()
