"""Debug script to check database schema and run insertions."""
import sqlite3
from app import app
from models import db, Bolsista

# Check schema
conn = sqlite3.connect('instance/gestao_editais_new.db')
c = conn.cursor()
c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='bolsistas'")
row = c.fetchone()
if row:
    # Check for UNIQUE on cpf
    sql = row[0]
    if 'UNIQUE' in sql and 'cpf' in sql:
        print("[ALERTA] A tabela bolsistas ainda tem UNIQUE constraint no CPF!")
        print("Isso precisa ser removido manualmente via migração.")
        print()
        print("SQL da tabela:")
        print(sql[:500])
    else:
        print("[OK] Nenhuma constraint UNIQUE no campo CPF encontrada no schema.")
else:
    print("[ERRO] Tabela bolsistas nao encontrada!")

# Check indexes
c.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='bolsistas'")
indexes = c.fetchall()
print("\nIndices na tabela bolsistas:")
for idx in indexes:
    print(f"  - {idx[0]}: {idx[1]}")
    if idx[1] and 'cpf' in idx[1].lower() and 'unique' in idx[1].lower():
        print("    ^ ESTE INDEX IMPEDE DUPLICATAS DE CPF!")

conn.close()
