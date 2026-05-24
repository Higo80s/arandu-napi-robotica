import sqlite3
import os
import db

# Test 1: Verificar estrutura
db_path = os.path.join(os.path.dirname(__file__), 'gestao_editais.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='editais'")
result = c.fetchone()
if result:
    print("Schema de editais:")
    print(result[0])
    print()

# Test 2: Verificar dados existentes
c.execute("SELECT COUNT(*) FROM editais")
count = c.fetchone()[0]
print(f"Editais no banco: {count}")
print()

# Test 3: Tentar inserir novo edital
print("Testando inserção...")
try:
    novo_id = db.criar_edital(
        numero="TEST-001/2025",
        descricao="Teste de inserção",
        agencia="Teste",
        codigo_projeto=None,
        descricao_projeto=None
    )
    print(f"✅ Edital criado com ID: {novo_id}")
    
    # Verificar se realmente foi salvo
    c.execute("SELECT * FROM editais WHERE id = ?", (novo_id,))
    resultado = c.fetchone()
    if resultado:
        print(f"✅ Dados confirmados no banco: {resultado}")
    else:
        print("❌ ERRO: Dados não encontrados após INSERT!")
        
except Exception as e:
    print(f"❌ Erro ao criar edital: {e}")
    import traceback
    traceback.print_exc()

conn.close()
