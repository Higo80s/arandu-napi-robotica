"""
Migration Script: Remove UNIQUE constraint from CPF column
SQLite does not support ALTER TABLE DROP CONSTRAINT, so we need to recreate the table.
"""
import sqlite3
import shutil
from datetime import datetime

DB_PATH = 'instance/gestao_editais_new.db'
BACKUP_PATH = f'instance/gestao_editais_new_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'

def migrate():
    # STEP 1: Create backup
    print(f"[1/5] Criando backup: {BACKUP_PATH}")
    shutil.copy(DB_PATH, BACKUP_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # STEP 2: Get current schema
    print("[2/5] Obtendo schema atual...")
    c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='bolsistas'")
    old_schema = c.fetchone()[0]
    
    # STEP 3: Create new schema without UNIQUE on cpf
    # Replace the UNIQUE constraint
    new_schema = old_schema.replace('cpf VARCHAR(14) UNIQUE', 'cpf VARCHAR(14)')
    new_schema = new_schema.replace('bolsistas', 'bolsistas_new')
    
    print("[3/5] Criando nova tabela sem constraint UNIQUE...")
    c.execute(new_schema)
    
    # STEP 4: Copy data
    print("[4/5] Copiando dados...")
    c.execute("INSERT INTO bolsistas_new SELECT * FROM bolsistas")
    
    # STEP 5: Swap tables
    print("[5/5] Substituindo tabela original...")
    c.execute("DROP TABLE bolsistas")
    c.execute("ALTER TABLE bolsistas_new RENAME TO bolsistas")
    
    conn.commit()
    conn.close()
    
    print("\n[OK] Migracao concluida com sucesso!")
    print(f"Backup salvo em: {BACKUP_PATH}")
    print("O campo CPF agora permite duplicatas (multiplos vinculos por discente).")

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACAO V16: Remover UNIQUE constraint do CPF")
    print("=" * 60)
    migrate()
