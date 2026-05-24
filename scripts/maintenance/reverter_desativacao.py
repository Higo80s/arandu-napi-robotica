# Script para REVERTER - Reativar todos do Edital 13 que foram desativados

import sqlite3

conn = sqlite3.connect('instance/gestao_editais_new.db')
cursor = conn.cursor()

print("=== REVERTENDO - Reativando bolsistas Edital 13 ===\n")

cursor.execute("""
    UPDATE bolsistas 
    SET ativo = 1, motivo_desligamento = NULL
    WHERE edital_id = 13
""")

conn.commit()
linhas_afetadas = cursor.rowcount
print(f"✅ {linhas_afetadas} bolsistas reativados!")

conn.close()
