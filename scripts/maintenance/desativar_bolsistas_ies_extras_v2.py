# Script CORRIGIDO para desativar bolsistas IES que não estão realmente ativos

import sqlite3

conn = sqlite3.connect('instance/gestao_editais_new.db')
cursor = conn.cursor()

print("=== BOLSISTAS EDITAL 13 PARA DESATIVAR ===\n")

# Lista dos 16 CPFs que devem permanecer ativos
cpfs_ativos = [
    '06411202907',  # ALINE FERNANDA CAMPAGNARO
    '13179671947',  # ANA CAROLINA MONTEIRO
    '09841699974',  # Ana Claudia Lazaroto
    '06789013920',  # BERNARD MENE
    '00792579925',  # CARLA FERNANDA MAREK
    '10042916984',  # DANKA FARIAS DE OLIVEIRA
    '04209369390',  # GUILHERME SEVERO MEDEIROS
    '01001446917',  # ISABELA DA SILVA LEONARDO
    '13325537960',  # JAINARA BAPTISTA GASPAR
    '07892927930',  # MARCUS VINICIUS DA SILVA RODRIGUES
    '098597011113',  # MATEUS MOISES MUTOCOLA
    '12608712908',  # MATHEUS BUENO BARTKEVICIUS
    '06520994910',  # SUZANA STRUIVING
    '03515367365',  # THEMIS RAQUEL DE JESUS DE OLIVEIRA
    '03537154682',  # VIVIAN PRADO DE CAMARGO LEAO
    '07525334951',  # GABRIELA WOLHMUTH (Finalizando)
]

# Criar placeholders para SQL
placeholders = ','.join(['?'] * len(cpfs_ativos))

# Verificar quantos serão desativados
cursor.execute(f"""
    SELECT COUNT(*) FROM bolsistas 
    WHERE edital_id = 13 AND ativo = 1 AND cpf NOT IN ({placeholders})
""", cpfs_ativos)

total_desativar = cursor.fetchone()[0]
print(f"Bolsistas atualmente com ativo=1: 59")
print(f"Bolsistas que devem permanecer ativos: {len(cpfs_ativos)}")
print(f"Bolsistas que serão desativados: {total_desativar}\n")

if total_desativar == 0:
    print("✅ Nenhum bolsista para desativar. Dados já estão corretos!")
    conn.close()
    exit()

# Listar os que serão desativados
cursor.execute(f"""
    SELECT nome, cpf FROM bolsistas 
    WHERE edital_id = 13 AND ativo = 1 AND cpf NOT IN ({placeholders})
    ORDER BY nome
""", cpfs_ativos)

print("Bolsistas que serão marcados como INATIVOS:\n")
for idx, row in enumerate(cursor.fetchall(), 1):
    print(f"  {idx}. {row[0]} (CPF: {row[1]})")

# Confirmar
print(f"\n{'='*60}")
resposta = input(f"Deseja desativar {total_desativar} bolsistas? (s/N): ")

if resposta.lower() == 's':
    cursor.execute(f"""
        UPDATE bolsistas 
        SET ativo = 0, motivo_desligamento = 'Outros'
        WHERE edital_id = 13 AND ativo = 1 AND cpf NOT IN ({placeholders})
    """, cpfs_ativos)
    
    conn.commit()
    print(f"\n✅ {total_desativar} bolsistas desativados com sucesso!")
    print(f"✅ 16 bolsistas permaneceram ativos.")
else:
    print("\n❌ Operação cancelada.")

conn.close()
