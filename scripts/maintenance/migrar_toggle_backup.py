"""
Script de Migração: Adicionar coluna data_fim_bolsa_backup
Para toggle ativo/inativo com memória
"""

import sqlite3
from datetime import datetime

# Conectar ao banco
conn = sqlite3.connect('instance/gestao_editais_new.db')
cursor = conn.cursor()

print("=== MIGRAÇÃO: Adicionar data_fim_bolsa_backup ===\n")

try:
    # Verificar se coluna já existe
    cursor.execute("PRAGMA table_info(bolsistas)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'data_fim_bolsa_backup' in columns:
        print("✅ Coluna data_fim_bolsa_backup já existe!")
    else:
        print("Adicionando coluna data_fim_bolsa_backup...")
        cursor.execute("ALTER TABLE bolsistas ADD COLUMN data_fim_bolsa_backup DATE")
        conn.commit()
        print("✅ Coluna adicionada com sucesso!")
    
    print("\n=== MIGRAÇÃO CONCLUÍDA ===")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    conn.rollback()

finally:
    conn.close()
