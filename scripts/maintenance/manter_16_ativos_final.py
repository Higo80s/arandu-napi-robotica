# Script FINAL CORRIGIDO - Manter apenas os 16 bolsistas ativos

import sqlite3

conn = sqlite3.connect('instance/gestao_editais_new.db')
cursor = conn.cursor()

print("=== MANTENDO APENAS 16 BOLSISTAS ATIVOS ===\n")

# Lista dos 16 CPFs que devem permanecer ativos
cpfs_manter_ativos = [
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
    '09859701113',  # MATEUS MOISES MUTOCOLA
    '12608712908',  # MATHEUS BUENO BARTKEVICIUS
    '06520994910',  # SUZANA STRUIVING
    '03515367365',  # THEMIS RAQUEL DE JESUS DE OLIVEIRA
    '03537154682',  # VIVIAN PRADO DE CAMARGO LEAO
    '07525334951',  # GABRIELA WOLHMUTH (Finalizando)
]

# Passo 1: Desativar TODOS do edital 13
cursor.execute("""
    UPDATE bolsistas 
    SET ativo = 0, motivo_desligamento = 'Outros'
    WHERE edital_id = 13
""")

print(f"Passo 1: Todos desativados temporariamente")

# Passo 2: Reativar APENAS os 16
placeholders = ','.join(['?'] * len(cpfs_manter_ativos))
cursor.execute(f"""
    UPDATE bolsistas 
    SET ativo = 1, motivo_desligamento = NULL
    WHERE edital_id = 13 AND cpf IN ({placeholders})
""", cpfs_manter_ativos)

conn.commit()

# Verificar resultado
cursor.execute("SELECT COUNT(*) FROM bolsistas WHERE edital_id = 13 AND ativo = 1")
ativos = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM bolsistas WHERE edital_id = 13 AND ativo = 0")
inativos = cursor.fetchone()[0]

print(f"\nPasso 2: Reativados os 16 corretos")
print(f"\n{'='*60}")
print(f"✅ RESULTADO FINAL:")
print(f"   - Bolsistas ATIVOS: {ativos}")
print(f"   - Bolsistas INATIVOS: {inativos}")
print(f"   - Total: {ativos + inativos}")

if ativos == 16:
    print(f"\n✅ SUCESSO! Exatamente 16 bolsistas ativos!")
else:
    print(f"\n⚠️  ATENÇÃO: Esperava 16 ativos, mas tem {ativos}!")

conn.close()
