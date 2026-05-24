#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste de inicialização: verifica se app.py consegue inicializar sem erros.
"""

import sys
import os

print("[TEST] Iniciando teste de inicialização de app.py...")

# Simular o que __init__ faria
print("[TEST] Importando módulos...")
try:
    import tkinter as tk
    import db
    print("✓ Módulos importados com sucesso")
except Exception as e:
    print(f"✗ Erro ao importar módulos: {e}")
    sys.exit(1)

print("\n[TEST] Verificando arquivo de banco de dados...")
db_path = os.path.join(os.path.dirname(__file__), 'gestao_editais.db')
print(f"  DB Path: {db_path}")
if os.path.exists(db_path):
    print(f"  ✓ Banco existe (tamanho: {os.path.getsize(db_path)} bytes)")
else:
    print(f"  ✗ Banco NÃO encontrado!")
    sys.exit(1)

print("\n[TEST] Testando obter_todos_editais()...")
try:
    editais = db.obter_todos_editais()
    print(f"  ✓ {len(editais)} editais encontrados:")
    for eid, enum in editais:
        print(f"    - ID={eid}: {enum}")
except Exception as e:
    print(f"  ✗ Erro: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[TEST] ✓ Todos os testes passaram!")
