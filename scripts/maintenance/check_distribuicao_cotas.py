import sqlite3
import pandas as pd

# Conectar ao SQLite
conn = sqlite3.connect('instance/gestao_editais_new.db')

# Verificar se tabela existe
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='distribuicao_cotas'")
exists = cursor.fetchone()

if exists:
    print("Tabela 'distribuicao_cotas' EXISTE no SQLite")
    
    # Ver estrutura
    cursor.execute("PRAGMA table_info(distribuicao_cotas)")
    columns = cursor.fetchall()
    print("\nColunas:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Contar registros
    cursor.execute("SELECT COUNT(*) FROM distribuicao_cotas")
    count = cursor.fetchone()[0]
    print(f"\nTotal de registros: {count}")
    
    # Exportar dados
    df = pd.read_sql_query("SELECT * FROM distribuicao_cotas", conn)
    df.to_csv('distribuicao_cotas_backup.csv', index=False)
    print(f"\nDados exportados para 'distribuicao_cotas_backup.csv'")
else:
    print("Tabela 'distribuicao_cotas' NÃO EXISTE no SQLite")

conn.close()
