import sqlite3
import os
import db
from datetime import datetime

# Inserir edital de teste com timestamp para unicidade
now = datetime.now().strftime('%Y%m%d%H%M%S')
numero = f"TEST-TRY-{now}"
descricao = "Teste automático Try Again"
agencia = "TesteUnit"

print('Inserindo edital de teste:', numero)
try:
    novo_id = db.criar_edital(numero, descricao, agencia, None, None)
    print('Inserido com ID:', novo_id)
except Exception as e:
    print('Erro ao inserir:', e)

# Consultar usando mesma query da UI
db_path = os.path.join(os.path.dirname(__file__), 'gestao_editais.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT id, numero_edital FROM editais ORDER BY id")
rows = cur.fetchall()
print('\nLista de editais (id, numero):')
for r in rows[-10:]:  # Mostrar últimos 10
    print(r)

# Verificar presença do nosso edital
cur.execute("SELECT id FROM editais WHERE numero_edital = ?", (numero,))
found = cur.fetchone()
if found:
    print('\nVerificacao: OK - edital encontrado no DB com id', found[0])
else:
    print('\nVerificacao: FALHA - edital NAO encontrado no DB')

conn.close()
