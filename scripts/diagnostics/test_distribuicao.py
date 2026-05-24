#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste de Distribuição: Valida que o executável usará o banco correto
"""

import os
import shutil

print("="*60)
print("VALIDAÇÃO DE DISTRIBUIÇÃO")
print("="*60)

# Pasta do projeto
project_dir = r'C:\Users\higosantos\Documents\gestao_editais'
dist_dir = os.path.join(project_dir, 'dist')
exe_path = os.path.join(dist_dir, 'GestaoEditais.exe')
bank_in_project = os.path.join(project_dir, 'gestao_editais.db')
bank_in_dist = os.path.join(dist_dir, 'gestao_editais.db')

print(f"\n[1] Verificando Executável")
if os.path.exists(exe_path):
    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    print(f"    ✓ {exe_path}")
    print(f"      Tamanho: {size_mb:.1f} MB")
else:
    print(f"    ✗ ERRO: Executável não encontrado")
    exit(1)

print(f"\n[2] Verificando Banco no Projeto")
if os.path.exists(bank_in_project):
    size_kb = os.path.getsize(bank_in_project) / 1024
    print(f"    ✓ {bank_in_project}")
    print(f"      Tamanho: {size_kb:.1f} KB")
else:
    print(f"    ✗ ERRO: Banco não encontrado no projeto")
    exit(1)

print(f"\n[3] Verificando Banco em dist/")
if os.path.exists(bank_in_dist):
    size_kb = os.path.getsize(bank_in_dist) / 1024
    print(f"    ✓ {bank_in_dist}")
    print(f"      Tamanho: {size_kb:.1f} KB")
else:
    print(f"    ⚠ Banco NÃO está em dist/")
    print(f"    Copiando...")
    try:
        shutil.copy(bank_in_project, bank_in_dist)
        print(f"    ✓ Banco copiado com sucesso!")
    except Exception as e:
        print(f"    ✗ ERRO ao copiar: {e}")
        exit(1)

print(f"\n[4] Estrutura de Distribuição")
print(f"    dist/")
for item in os.listdir(dist_dir):
    item_path = os.path.join(dist_dir, item)
    if os.path.isfile(item_path):
        size_mb = os.path.getsize(item_path) / (1024 * 1024)
        print(f"      - {item} ({size_mb:.1f} MB)")
    else:
        print(f"      - {item}/ (pasta)")

print(f"\n[5] Instruções de Distribuição")
print(f"""
Para distribuir a aplicação:

1. Copiar a pasta 'dist' completa:
   Copiar: C:\\Users\\higosantos\\Documents\\gestao_editais\\dist\\
   Para: Onde você quiser distribuir (ex: Pendrive, pasta de rede, etc)

2. A pasta 'dist' deve conter:
   - GestaoEditais.exe (executável)
   - gestao_editais.db (banco de dados)

3. Para usar:
   - Duplo-clique em GestaoEditais.exe
   - Os dados serão salvos em gestao_editais.db (na mesma pasta)

⚠ IMPORTANTE:
   - Nunca mude de local o gestao_editais.db
   - Sempre mante na mesma pasta do .exe
   - Os dados salvos serão persistidos no disco
""")

print("="*60)
print("✅ Validação Completa - Pronto para Distribuição!")
print("="*60)
