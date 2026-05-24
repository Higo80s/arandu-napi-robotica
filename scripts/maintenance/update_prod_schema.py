import sqlite3
import os

# Production DB Path
db_path = 'instance/gestao_editais_new.db'

if not os.path.exists(db_path):
    print(f"Banco de dados não encontrado em: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE bolsistas ADD COLUMN projeto_pesquisa TEXT")
    print("Coluna 'projeto_pesquisa' adicionada.")
except Exception as e:
    print(f"Nota: Coluna 'projeto_pesquisa' já deve existir ou erro: {e}")

try:
    cursor.execute("ALTER TABLE bolsistas ADD COLUMN recebe_bolsa BOOLEAN")
    print("Coluna 'recebe_bolsa' adicionada.")
except Exception as e:
    print(f"Nota: Coluna 'recebe_bolsa' já deve existir ou erro: {e}")

conn.commit()
conn.close()
