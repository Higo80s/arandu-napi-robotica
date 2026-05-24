"""
Migration V16b: Fix foreign key reference from programa_academico_old to programa_academico
"""
import sqlite3
import shutil
from datetime import datetime

DB_PATH = 'instance/gestao_editais_new.db'
BACKUP_PATH = f'instance/gestao_editais_backup_v16b_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'

def migrate():
    print(f"[1/6] Criando backup: {BACKUP_PATH}")
    shutil.copy(DB_PATH, BACKUP_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print("[2/6] Obtendo schema atual da tabela bolsistas...")
    c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='bolsistas'")
    old_schema = c.fetchone()[0]
    print(f"     Schema atual tem {len(old_schema)} caracteres")
    
    # Fix the foreign key reference
    if 'programa_academico_old' in old_schema:
        new_schema = old_schema.replace('programa_academico_old', 'programa_academico')
        print("[3/6] Corrigindo foreign key: programa_academico_old -> programa_academico")
    else:
        print("[3/6] Foreign key ja esta correta, verificando outras issues...")
        new_schema = old_schema
    
    # Rename for new table
    new_schema = new_schema.replace('CREATE TABLE bolsistas', 'CREATE TABLE bolsistas_new')
    
    # Cleanup any leftover temp table
    c.execute("DROP TABLE IF EXISTS bolsistas_new")
    
    print("[4/6] Criando nova tabela...")
    c.execute(new_schema)
    
    print("[5/6] Copiando dados...")
    c.execute("INSERT INTO bolsistas_new SELECT * FROM bolsistas")
    
    print("[6/6] Substituindo tabela original...")
    c.execute("DROP TABLE bolsistas")
    c.execute("ALTER TABLE bolsistas_new RENAME TO bolsistas")
    
    conn.commit()
    conn.close()
    
    print("\n[OK] Migracao V16b concluida!")
    print(f"Backup: {BACKUP_PATH}")

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACAO V16b: Corrigir FK programa_academico")
    print("=" * 60)
    migrate()
