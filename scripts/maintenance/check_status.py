import sqlite3

conn = sqlite3.connect('instance/gestao_editais_new.db')
cursor = conn.cursor()

print("=== STATUS ATUAL EDITAL 13 ===\n")

cursor.execute("SELECT ativo, COUNT(*) FROM bolsistas WHERE edital_id = 13 GROUP BY ativo")
for row in cursor.fetchall():
    status = "ATIVO" if row[0] == 1 else "IN ATIVO"
    print(f"{status}: {row[1]} bolsistas")

print("\n=== LISTA DE ATIVOS ===\n")
cursor.execute("SELECT nome, cpf FROM bolsistas WHERE edital_id = 13 AND ativo = 1")
ativos = cursor.fetchall()

if len(ativos) == 0:
    print("⚠️  NENHUM BOLSISTA ATIVO!")
else:
    for idx, row in enumerate(ativos, 1):
        print(f"{idx}. {row[0]} - CPF: {row[1]}")

conn.close()
