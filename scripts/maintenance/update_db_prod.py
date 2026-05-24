import sqlite3
import os

db_path = 'instance/gestao_editais_new.db'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check and Add 'agencia_fomento'
try:
    cursor.execute("ALTER TABLE bolsistas ADD COLUMN agencia_fomento TEXT")
    print("Column 'agencia_fomento' added.")
except sqlite3.OperationalError:
    print("Column 'agencia_fomento' already exists.")

# Check and Add 'projeto_pesquisa' (Just in case)
try:
    cursor.execute("ALTER TABLE bolsistas ADD COLUMN projeto_pesquisa TEXT")
    print("Column 'projeto_pesquisa' added.")
except sqlite3.OperationalError:
    print("Column 'projeto_pesquisa' already exists.")

# Check and Add 'recebe_bolsa' (Just in case)
try:
    cursor.execute("ALTER TABLE bolsistas ADD COLUMN recebe_bolsa BOOLEAN")
    print("Column 'recebe_bolsa' added.")
except sqlite3.OperationalError:
    print("Column 'recebe_bolsa' already exists.")

conn.commit()
conn.close()
