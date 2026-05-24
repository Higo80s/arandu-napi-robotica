#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste de Validação Final - Persistência e UI
Valida que:
1. Dados persistem no banco
2. App carrega dados ao iniciar
3. Novo edital pode ser criado
"""

import os
import sys
from datetime import datetime

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(__file__))

import db
import sqlite3

print("="*60)
print("TESTE DE VALIDAÇÃO FINAL - PERSISTÊNCIA")
print("="*60)

db_path = os.path.join(os.path.dirname(__file__), 'gestao_editais.db')

# ============ TESTE 1: Verificar banco existe ============
print("\n[1/5] Verificando banco de dados...")
if os.path.exists(db_path):
    size = os.path.getsize(db_path)
    print(f"    ✓ Banco encontrado: {size} bytes")
else:
    print(f"    ✗ ERRO: Banco não encontrado em {db_path}")
    sys.exit(1)

# ============ TESTE 2: Listar editais existentes ============
print("\n[2/5] Listando editais existentes...")
try:
    editais = db.obter_todos_editais()
    print(f"    ✓ {len(editais)} editais encontrados:")
    for eid, enum in editais:
        print(f"      - ID {eid}: {enum}")
except Exception as e:
    print(f"    ✗ ERRO ao listar: {e}")
    sys.exit(1)

# ============ TESTE 3: Criar novo edital ============
print("\n[3/5] Criando novo edital de teste...")
numero_teste = f"VALIDACAO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
try:
    novo_id = db.criar_edital(
        numero_teste,
        "Edital de Validação Final",
        "Teste",
        None,
        None
    )
    print(f"    ✓ Edital criado com ID: {novo_id}")
except Exception as e:
    print(f"    ✗ ERRO ao criar: {e}")
    sys.exit(1)

# ============ TESTE 4: Verificar persistência imediata ============
print("\n[4/5] Verificando persistência (imediatamente após criar)...")
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, numero_edital FROM editais WHERE numero_edital = ?",
        (numero_teste,)
    )
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        print(f"    ✓ Edital encontrado no banco: ID={resultado[0]}, Número={resultado[1]}")
    else:
        print(f"    ✗ ERRO: Edital não encontrado (problema de persistência!)")
        sys.exit(1)
except Exception as e:
    print(f"    ✗ ERRO: {e}")
    sys.exit(1)

# ============ TESTE 5: Verificar com obter_todos_editais() ============
print("\n[5/5] Verificando com função de carregamento de UI...")
try:
    editais_reload = db.obter_todos_editais()
    encontrado = any(e[1] == numero_teste for e in editais_reload)
    
    if encontrado:
        print(f"    ✓ Edital aparece na lista de carregamento da UI")
    else:
        print(f"    ✗ ERRO: Edital não aparece na lista de UI (problema de carregamento!)")
        sys.exit(1)
except Exception as e:
    print(f"    ✗ ERRO: {e}")
    sys.exit(1)

# ============ RESUMO ============
print("\n" + "="*60)
print("✓ TODOS OS TESTES PASSARAM!")
print("="*60)
print("\nResumo:")
print("  • Banco de dados: OK")
print("  • Persistência: OK")
print("  • Carregamento: OK")
print("  • Novo edital: OK")
print("\nO sistema está pronto para uso!")
