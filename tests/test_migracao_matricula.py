import pytest
from unittest.mock import patch, MagicMock
import psycopg2
from psycopg2 import OperationalError, DatabaseError

# O módulo deve estar acessível por PYTHONPATH ou ser testado no mesmo contexto
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.migracao_matricula import MigrationCommand, AddMatriculaStrategy

# ==========================================
# TESTES UNITÁRIOS - FIXTURES E MOCKS
# ==========================================

@pytest.fixture
def mock_strategy():
    strategy = MagicMock()
    strategy.get_sql.return_value = "ALTER TABLE fake_table ADD COLUMN fake_col VARCHAR(10);"
    strategy.get_undo_sql.return_value = "ALTER TABLE fake_table DROP COLUMN fake_col;"
    return strategy

@pytest.fixture
def mock_db_url():
    return "postgresql://user:pass@localhost/db_test"

# 1. HAPPY PATH TEST
@patch('scripts.migracao_matricula.psycopg2.connect')
def test_migration_execute_happy_path(mock_connect, mock_db_url, mock_strategy):
    """Testa a execução suave onde tudo ocorre conforme o esperado."""
    # Simula a conexão com DDL válido e Commit bem sucedido
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    command = MigrationCommand(mock_db_url, mock_strategy)
    result = command.execute()

    assert result is True
    mock_connect.assert_called_once()
    mock_cursor.execute.assert_called_once_with(mock_strategy.get_sql())
    mock_conn.commit.assert_called_once()

# 2. EDGE CASE: DATABASE FORA DO AR (TIMEOUT)
@patch('scripts.migracao_matricula.psycopg2.connect')
def test_migration_execute_database_down(mock_connect, mock_db_url, mock_strategy):
    """Garante que OperationalError (Timeout) é capturado graciosamente sem travar."""
    mock_connect.side_effect = OperationalError("Connection Timed Out")

    command = MigrationCommand(mock_db_url, mock_strategy)
    result = command.execute()

    assert result is False

# 3. EDGE CASE: SINTAXE SQL INVÁLIDA (ROLLBACK)
@patch('scripts.migracao_matricula.psycopg2.connect')
def test_migration_execute_invalid_syntax(mock_connect, mock_db_url, mock_strategy):
    """Garante que se falhar no meio da query, o Rollback será invocado no bloco de Try-Except."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = DatabaseError("Syntax Error at line 1")
    
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    command = MigrationCommand(mock_db_url, mock_strategy)
    result = command.execute()

    assert result is False
    mock_conn.rollback.assert_called_once()

# 4. EDGE CASE: INVALID URL (ENV ISSUE)
def test_migration_invalid_environment_url(mock_strategy):
    """Garante falha imediata na instanciação se variável de ambiente não existir."""
    with pytest.raises(ValueError, match="DATABASE_URL não configurada no ambiente."):
        MigrationCommand("", mock_strategy)
