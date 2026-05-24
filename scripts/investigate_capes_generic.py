"""
Script para investigar os códigos que ainda estão como 'CAPES' genérica
e redistribuir para CAPES PPG ou CAPES IES PROPPG conforme planilhas oficiais
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

# Códigos reportados pelo usuário que estão como "CAPES" genérica
CODIGOS_PROBLEMA = [
    '40006018001P1',  # CPGEI
    '40002012171P9',  # PPGAEE
    '40006018005P7',  # PPGAG
    '40006018180P3',  # PPGBIO
    '40006018037P6',  # PPGBIOINFO
    '40006018176P6',  # PPGBIOTEC
    '40006018182P6',  # PPGCC
    '40006018171P4',  # PPGCC
    '40006018175P0',  # PPGCEM
    '40006018013P0',  # PPGCTA
    '40006018184P9',  # PPGDP
    '40006018010P0',  # PPGDR
    '40006018032P1',  # PPGEA (FB)
    '40006018174P3',  # PPGEA (FB)
    '40006018023P5',  # PPGEA (LD)
    '40006018008P6',  # PPGEC (CT)
    '40006018030P1',  # PPGEC (PB)
    '40006018044P0',  # PPGEC (PB)
    '40006018006P3',  # PPGECT
    '40006018044P2',  # PPGA
]

print("="*80)
print("INVESTIGAÇÃO DOS CÓDIGOS COM 'CAPES' GENÉRICA")
print("="*80)
print()

# Ler dados oficiais
df = pd.read_csv('dados_planilhas_oficiais.csv', encoding='utf-8-sig')

print(f"Total de registros nas planilhas oficiais: {len(df)}")
print()

# Filtrar pelos códigos problemáticos
df_problema = df[df['codigo'].isin(CODIGOS_PROBLEMA)]

print(f"Registros encontrados para os códigos problemáticos: {len(df_problema)}")
print()

# Agrupar por código e agência original
print("="*80)
print("DISTRIBUIÇÃO POR CÓDIGO E TIPO DE CAPES")
print("="*80)
print()

for codigo in CODIGOS_PROBLEMA:
    df_codigo = df_problema[df_problema['codigo'] == codigo]
    
    if len(df_codigo) == 0:
        print(f"{codigo}: NÃO ENCONTRADO nas planilhas oficiais")
        continue
    
    print(f"\n{codigo}:")
    print(f"  Total de registros: {len(df_codigo)}")
    
    # Ver distribuição por agência original
    agencias = df_codigo.groupby('agencia_original')['quantidade'].agg(['count', 'sum'])
    
    for ag, row in agencias.iterrows():
        print(f"  - {ag}: {row['count']} registros, soma={row['sum']}")
    
    # Ver alguns exemplos
    print(f"\n  Exemplos:")
    for idx, row in df_codigo.head(3).iterrows():
        print(f"    {row['nivel']}, {row['ano']}, {row['agencia_original']}: qtd={row['quantidade']}")

print()
print("="*80)
print("CONCLUSÃO")
print("="*80)
print()

# Ver quais códigos têm capes_ppg vs capes_ies_proppg
tem_ppg = df_problema[df_problema['agencia_original'] == 'capes_ppg']['codigo'].unique()
tem_ies = df_problema[df_problema['agencia_original'] == 'capes_ies_proppg']['codigo'].unique()

print(f"Códigos com 'capes_ppg': {len(tem_ppg)}")
for c in tem_ppg:
    print(f"  - {c}")

print(f"\nCódigos com 'capes_ies_proppg': {len(tem_ies)}")
for c in tem_ies:
    print(f"  - {c}")

# Códigos que não estão nas planilhas
nao_encontrados = set(CODIGOS_PROBLEMA) - set(df_problema['codigo'].unique())
if nao_encontrados:
    print(f"\nCódigos NÃO encontrados nas planilhas: {len(nao_encontrados)}")
    for c in nao_encontrados:
        print(f"  - {c}")
