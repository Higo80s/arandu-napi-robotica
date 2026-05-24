import sqlite3

conn = sqlite3.connect('instance/gestao_editais_new.db')
cursor = conn.cursor()

print("=== IDENTIFICANDO OS 16 BOLSISTAS IES CORRETOS ===\n")

# Lista dos 16 nomes conforme extraídos pelo browser
nomes_ativos = [
    'ALINE FERNANDA CAMPAGNARO',
    'ANA CAROLINA MONTEIRO',
    'Ana Claudia Lazaroto',
    'BERNARD MENE',
    'CARLA FERNANDA MAREK',
    'DANKA FARIAS DE OLIVEIRA',
    'GUILHERME SEVERO MEDEIROS',
    'ISABELA DA SILVA LEONARDO',
    'JAINARA BAPTISTA GASPAR',
    'MARCUS VINICIUS DA SILVA RODRIGUES',
    'MATEUS MOISES MUTOCOLA',
    'MATHEUS BUENO BARTKEVICIUS',
    'SUZANA STRUIVING',
    'THEMIS RAQUEL DE JESUS DE OLIVEIRA',
    'VIVIAN PRADO DE CAMARGO LEAO',
    'GABRIELA WOLHMUTH'
]

# Buscar IDs por nome (case-insensitive)
ids_manter_ativos = []
print("Bolsistas encontrados:\n")

for nome in nomes_ativos:
    cursor.execute("""
        SELECT id, nome, cpf 
        FROM bolsistas 
        WHERE edital_id = 13 AND UPPER(nome) LIKE UPPER(?)
    """, (f'%{nome}%',))
    
    result = cursor.fetchone()
    if result:
        ids_manter_ativos.append(result[0])
        print(f"  ✅ ID {result[0]:3d} - {result[1]} (CPF: {result[2]})")
    else:
        print(f"  ❌ NÃO ENCONTRADO: {nome}")

print(f"\n{'='*60}")
print(f"Total de IDs encontrados: {len(ids_manter_ativos)}")

if len(ids_manter_ativos) != 16:
    print(f"⚠️  ATENÇÃO: Esperava 16 IDs, mas encontrou {len(ids_manter_ativos)}!")
    print("\nVerifique os nomes que não foram encontrados e ajuste manualmente.")
    conn.close()
    exit()

# Passo 1: Desativar TODOS do edital 13
print(f"\nPasso 1: Desativando todos do Edital 13...")
cursor.execute("""
    UPDATE bolsistas 
    SET ativo = 0, motivo_desligamento = 'Outros'
    WHERE edital_id = 13
""")

# Passo 2: Reativar APENAS os 16 IDs
print(f"Passo 2: Reativando apenas os 16 bolsistas corretos...")
placeholders = ','.join(['?'] * len(ids_manter_ativos))
cursor.execute(f"""
    UPDATE bolsistas 
    SET ativo = 1, motivo_desligamento = NULL
    WHERE edital_id = 13 AND id IN ({placeholders})
""", ids_manter_ativos)

conn.commit()

# Verificar resultado
cursor.execute("SELECT COUNT(*) FROM bolsistas WHERE edital_id = 13 AND ativo = 1")
ativos = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM bolsistas WHERE edital_id = 13 AND ativo = 0")
inativos = cursor.fetchone()[0]

print(f"\n{'='*60}")
print(f"✅ CONCLUSÃO:")
print(f"   - Bolsistas ATIVOS: {ativos}")
print(f"   - Bolsistas INATIVOS: {inativos}")
print(f"   - Total: {ativos + inativos}")

if ativos == 16:
    print(f"\n🎉 SUCESSO! Exatamente 16 bolsistas ativos conforme esperado!")
    print(f"\nIDs reativados: {sorted(ids_manter_ativos)}")
else:
    print(f"\n⚠️  ATENÇÃO: Esperava 16 ativos, mas tem {ativos}!")

conn.close()
