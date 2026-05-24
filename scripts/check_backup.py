import sys
import os
import sqlite3
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Find backup
backup_files = [f for f in os.listdir('.') if f.startswith('gestao_editais_final.db.bak_20260227_')]
backup_file = max(backup_files)
print(f"Using backup: {backup_file}")

conn = sqlite3.connect(backup_file)
cur = conn.cursor()

target_names = [
    "JÚLIO CÉSAR RODRIGUES DE AZEVEDO",
    "ADALBERTO MATOSKI",
    "HIEDA MARIA PAGLIOSA CORONA", 
    "JULIO CAETANO TOMAZONI",
    "ELISETE GUIMARÃES",
    "ANTONIO CARLOS DE FRANCISCO"
]

print("Original locations in backup:")
for name in target_names:
    # Partial match
    name_parts = name.split()
    first_two = f"{name_parts[0]} {name_parts[1]}"
    cur.execute("SELECT id, nome, edital_id, modalidade_id, ativo FROM bolsistas WHERE nome LIKE ?", (f"%{first_two}%",))
    rows = cur.fetchall()
    for r in rows:
        print(f"Backup -> ID: {r[0]}, Nome: {r[1]}, Edital ID: {r[2]}, Modalidade: {r[3]}, Ativo: {r[4]}")

conn.close()
