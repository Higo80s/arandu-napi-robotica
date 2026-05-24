"""
Script para verificar se os programas faltantes têm dados reais nas planilhas oficiais
"""
import pandas as pd

# Códigos a verificar
CODIGOS = ['40006018014P6', '40006018029P3', '40006018185P5']

print("="*80)
print("VERIFICANDO PROGRAMAS NAS PLANILHAS OFICIAIS")
print("="*80)
print()

# Ler CSV dos dados oficiais
df = pd.read_csv('dados_planilhas_oficiais.csv', encoding='utf-8-sig')

for codigo in CODIGOS:
    print(f"\n{'='*80}")
    print(f"PROGRAMA: {codigo}")
    print('='*80)
    
    dados = df[df['codigo'] == codigo]
    
    if len(dados) == 0:
        print("  ❌ NÃO ENCONTRADO nas planilhas oficiais")
        continue
    
    print(f"  Total de registros: {len(dados)}")
    print()
    
    # Ver níveis
    niveis = dados['nivel'].unique()
    print(f"  Níveis: {', '.join(niveis)}")
    print()
    
    # Ver dados por nível e agência
    for nivel in niveis:
        dados_nivel = dados[dados['nivel'] == nivel]
        print(f"\n  {nivel}:")
        
        # Agrupar por agência
        for agencia in dados_nivel['agencia_original'].unique():
            dados_ag = dados_nivel[dados_nivel['agencia_original'] == agencia]
            
            # Ver quantidades por ano
            qtds = []
            anos = sorted(dados_ag['ano'].unique())
            
            for ano in anos:
                qtd = dados_ag[dados_ag['ano'] == ano]['quantidade'].sum()
                qtds.append(qtd)
            
            soma_total = sum(qtds)
            
            print(f"    {agencia}:")
            print(f"      Anos: {', '.join(map(str, anos))}")
            print(f"      Qtds: {', '.join(map(str, [int(q) for q in qtds]))}")
            print(f"      SOMA: {int(soma_total)}")
            
            if soma_total > 0:
                print(f"      ⚠️  TEM DADOS NÃO-ZERO!")

print()
print("="*80)
print("FIM DA VERIFICAÇÃO")
print("="*80)
