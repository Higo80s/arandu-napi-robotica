#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste de Persistência: Simula o problema relatado pelo usuário.
"""

import db
import sqlite3
import os
from datetime import datetime

db_path = os.path.join(os.path.dirname(__file__), 'gestao_editais.db')
db.init_db(db_path)
db.ensure_db_schema()

# 1. Inserir um novo edital
print("=== Teste 1: Inserir Novo Edital ===")
numero_teste = f"TEST-PERSIST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
resultado = db.criar_edital(numero_teste, "Edital de Teste Persistência", "CAPES", None, None)
print(f"Edital criado com ID: {resultado}")
print(f"Número: {numero_teste}")

# 2. Verificar se foi salvo no banco
print("\n=== Teste 2: Verificar Persistência (imediatamente) ===")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT id, numero_edital FROM editais WHERE numero_edital = ?", (numero_teste,))
resultado = cursor.fetchone()
if resultado:
    print(f"✓ Edital ENCONTRADO no banco: ID={resultado[0]}, Número={resultado[1]}")
else:
    print("✗ Edital NÃO encontrado no banco (ERRO!)")
conn.close()

# 3. Listar todos os editais
print("\n=== Teste 3: Listar Todos os Editais ===")
todos_editais = db.obter_todos_editais()
for eid, enum in todos_editais:
    print(f"  - ID={eid}: {enum}")

print("\n=== Conclusão ===")
print("Se o edital TEST-PERSIST-* aparece acima, a persistência está OK.")
print("Se não aparece, há um problema de commit/conexão em db.py")
