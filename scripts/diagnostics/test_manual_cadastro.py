#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste manual de cadastro - reproduzir o que o usuário faz
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

import db
import sqlite3

db_path = os.path.join(os.path.dirname(__file__), 'gestao_editais.db')

print("="*60)
print("TESTE MANUAL DE CADASTRO")
print("="*60)

# Simular cadastro do usuário
numero_novo = f"MANUAL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
descricao = "Edital Cadastrado Manualmente"
agencia = "CAPES"
codigo_projeto = None
descricao_projeto = None

print(f"\n[PASSO 1] Preparando dados de cadastro:")
print(f"  Número: {numero_novo}")
print(f"  Descrição: {descricao}")
print(f"  Agência: {agencia}")

# Passo 2: Chamar a função
print(f"\n[PASSO 2] Chamando db.criar_edital()...")
try:
    novo_id = db.criar_edital(numero_novo, descricao, agencia, codigo_projeto, descricao_projeto)
    print(f"  ✓ Retornou ID: {novo_id}")
except Exception as e:
    print(f"  ✗ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Passo 3: Verificar se foi salvo imediatamente
print(f"\n[PASSO 3] Verificando persistência (imediatamente)...")
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM editais WHERE numero_edital = ?", (numero_novo,))
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        print(f"  ✓ Encontrado no banco: {resultado}")
    else:
        print(f"  ✗ NÃO ENCONTRADO!")
        sys.exit(1)
except Exception as e:
    print(f"  ✗ ERRO ao verificar: {e}")
    sys.exit(1)

# Passo 4: Usar obter_todos_editais (como a UI faz)
print(f"\n[PASSO 4] Testando obter_todos_editais()...")
try:
    todos = db.obter_todos_editais()
    encontrado = any(t[1] == numero_novo for t in todos)
    if encontrado:
        print(f"  ✓ Edital aparece na lista")
    else:
        print(f"  ✗ Edital NÃO aparece na lista de carregamento")
        sys.exit(1)
except Exception as e:
    print(f"  ✗ ERRO: {e}")
    sys.exit(1)

# Passo 5: Simular fechar e reabrir (consultar novamente)
print(f"\n[PASSO 5] Simulando fechar e reabrir (nova consulta)...")
try:
    todos_reload = db.obter_todos_editais()
    encontrado_reload = any(t[1] == numero_novo for t in todos_reload)
    if encontrado_reload:
        print(f"  ✓ Edital AINDA aparece após 'reabrir'")
        print(f"\n✅ TESTE COMPLETO - TUDO OK!")
    else:
        print(f"  ✗ Edital DESAPARECEU após 'reabrir'")
        print(f"\n❌ PROBLEMA IDENTIFICADO!")
        sys.exit(1)
except Exception as e:
    print(f"  ✗ ERRO: {e}")
    sys.exit(1)

print("="*60)
