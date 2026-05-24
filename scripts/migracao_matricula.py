import os
import sys
import logging
from typing import Protocol
import psycopg2
from psycopg2 import OperationalError, DatabaseError
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==========================================
# 1. STRATEGY PATTERN (Lógica de Execução)
# ==========================================
class MigrationStrategy(Protocol):
    """Interface abstrata para suporte Múltiplas Estratégias de DB."""
    def get_sql(self) -> str:
        pass
    def get_undo_sql(self) -> str:
        pass

class AddMatriculaStrategy:
    """Estratégia 1: Adicionar colunas de Matrícula (Safely)"""
    def get_sql(self) -> str:
        return """
        ALTER TABLE candidaturas ADD COLUMN IF NOT EXISTS registro_academico VARCHAR(20);
        ALTER TABLE bolsistas ADD COLUMN IF NOT EXISTS registro_academico VARCHAR(20);
        """
    def get_undo_sql(self) -> str:
        return """
        ALTER TABLE candidaturas DROP COLUMN IF EXISTS registro_academico;
        ALTER TABLE bolsistas DROP COLUMN IF EXISTS registro_academico;
        """

# ==========================================
# 2. COMMAND PATTERN (Execução Transacional)
# ==========================================
class MigrationCommand:
    """Aciona a Database obedecendo aos Princípios SOLID via Injeção de Dependência."""
    
    def __init__(self, db_url: str, strategy: MigrationStrategy):
        if not db_url:
            raise ValueError("DATABASE_URL não configurada no ambiente.")
        self.db_url = db_url.replace('postgres://', 'postgresql://', 1)
        self.strategy = strategy

    def execute(self) -> bool:
        """Executa a estratégia principal tratando Timeouts e Erros Relacionais."""
        conn = None
        try:
            logger.info("Estabelecendo conexão com o banco de dados...")
            # Edge Case 1: Timeout de rede
            conn = psycopg2.connect(self.db_url, connect_timeout=5)
            
            with conn.cursor() as cursor:
                sql = self.strategy.get_sql()
                logger.info(f"Executando DDL: \n{sql.strip()}")
                cursor.execute(sql)
                
            conn.commit()
            logger.info("✅ DDL Executado com Sucesso. Commit realizado.")
            return True
        
        except OperationalError as e:
            # Edge Case 1 & 2 Tratados: Banco Fora do ar ou Credenciais Inválidas
            logger.error(f"❌ Falha de Conexão ou Timeout: {e}")
            return False
            
        except DatabaseError as e:
            # Edge Case 3 Tratado: Query Inválida / Locking
            logger.error(f"❌ Erro de Transação no Banco: {e}")
            if conn:
                logger.warning("Realizando Rollback da transação atual...")
                conn.rollback()
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro inesperado da aplicação: {e}")
            if conn:
                conn.rollback()
            return False
            
        finally:
            if conn:
                conn.close()

    def undo(self) -> bool:
        """Aciona reversão (Rollback Estutural)"""
        conn = None
        try:
            conn = psycopg2.connect(self.db_url, connect_timeout=5)
            with conn.cursor() as cursor:
                cursor.execute(self.strategy.get_undo_sql())
            conn.commit()
            logger.info("✅ Reversão (Undo) executada com Sucesso.")
            return True
        except Exception as e:
            logger.error(f"❌ Erro crítico no Undo: {e}")
            if conn: conn.rollback()
            return False

if __name__ == '__main__':
    # Inicialização (Inversion of Control)
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    database_url = os.getenv("DATABASE_URL")
    
    strategy = AddMatriculaStrategy()
    command = MigrationCommand(database_url, strategy)
    
    # Happy Path: Aciona o script
    if not command.execute():
        sys.exit(1)
