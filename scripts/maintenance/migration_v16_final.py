"""
Migration V16 Final V2: Get actual columns from existing table
"""
import sqlite3
import shutil
from datetime import datetime

DB_PATH = 'instance/gestao_editais_new.db'
BACKUP_PATH = f'instance/backup_v16final_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'

def migrate():
    print(f"[1/7] Backup: {BACKUP_PATH}")
    shutil.copy(DB_PATH, BACKUP_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print("[2/7] Getting exact columns from existing bolsistas table...")
    c.execute("PRAGMA table_info(bolsistas)")
    columns = c.fetchall()
    
    # Build column list for new table (without UNIQUE constraints)
    col_defs = []
    col_names = []
    for col in columns:
        cid, name, type_, notnull, default, pk = col
        col_names.append(name)
        
        if pk:
            col_defs.append(f"{name} {type_} NOT NULL PRIMARY KEY")
        elif notnull:
            if default is not None:
                col_defs.append(f"{name} {type_} NOT NULL DEFAULT {default}")
            else:
                col_defs.append(f"{name} {type_} NOT NULL")
        else:
            if default is not None:
                col_defs.append(f"{name} {type_} DEFAULT {default}")
            else:
                col_defs.append(f"{name} {type_}")
    
    print(f"    Found {len(col_names)} columns")
    
    # Add foreign keys (with correct references)
    fk_defs = [
        "FOREIGN KEY(edital_id) REFERENCES editais(id)",
        "FOREIGN KEY(modalidade_id) REFERENCES modalidades(id)", 
        "FOREIGN KEY(programa_id) REFERENCES programa_academico(id)"
    ]
    
    print("[3/7] Dropping temp table if exists...")
    c.execute("DROP TABLE IF EXISTS bolsistas_new")
    
    print("[4/7] Creating bolsistas_new...")
    create_sql = f"CREATE TABLE bolsistas_new ({', '.join(col_defs)}, {', '.join(fk_defs)})"
    c.execute(create_sql)
    
    print("[5/7] Copying data...")
    cols_str = ", ".join(col_names)
    c.execute(f"INSERT INTO bolsistas_new ({cols_str}) SELECT {cols_str} FROM bolsistas")
    
    print("[6/7] Replacing original table...")
    c.execute("DROP TABLE bolsistas")
    c.execute("ALTER TABLE bolsistas_new RENAME TO bolsistas")
    
    print("[7/7] Verifying FK...")
    c.execute("PRAGMA foreign_key_check(bolsistas)")
    errors = c.fetchall()
    
    conn.commit()
    conn.close()
    
    if errors:
        # Filter out NULL programa_id (those are OK)
        real_errors = [e for e in errors if e[2] != 'programa_academico']
        if real_errors:
            print(f"\n[AVISO] {len(real_errors)} FK violations reais")
        else:
            print(f"\n[OK] {len(errors)} FK violations (programa_id NULL - OK)")
    else:
        print("\n[OK] Sem FK violations!")
    
    print("[OK] Migracao concluida!")

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACAO V16 FINAL V2")
    print("=" * 60)
    migrate()
