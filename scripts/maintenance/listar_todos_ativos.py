"""
Busca TODOS os bolsistas ativos por edital
"""

from app import app
from models import Bolsista, Edital, Modalidade

with app.app_context():
    print("=== TODOS OS BOLSISTAS ATIVOS POR EDITAL ===\n")
    
    editais = Edital.query.all()
    
    total_geral = 0
    
    for edital in editais:
        ativos = Bolsista.query.filter_by(edital_id=edital.id, ativo=True).count()
        
        if ativos > 0:
            # Contar por nível
            mestrado = Bolsista.query.join(Modalidade).filter(
                Bolsista.edital_id == edital.id,
                Bolsista.ativo == True,
                Modalidade.nivel.ilike('%mestrado%')
            ).count()
            
            doutorado = Bolsista.query.join(Modalidade).filter(
                Bolsista.edital_id == edital.id,
                Bolsista.ativo == True,
                Modalidade.nivel.ilike('%doutorado%')
            ).count()
            
            total_geral += ativos
            
            # Limpar nome para exibição
            nome_limpo = edital.numero[:40].replace('\u00e7','c').replace('\u00e3','a').replace('\u00e1','a')
            agencia_limpa = edital.agencia[:12].replace('\u00e7','c').replace('\u00e3','a')
            
            print(f"{nome_limpo:40s} | {agencia_limpa:12s} | {mestrado:3d}M + {doutorado:3d}D = {ativos:3d} total")
    
    print(f"\n{'TOTAL GERAL':40s}   {'':12s}   {total_geral:3d} bolsistas ativos")
    
    print("\n=== ANALISE ===")
    print(f"Total no sistema: {total_geral}")
    print(f"Esperado CAPES:   429 (255M + 151D + 14M + 9D)")
    print(f"Diferenca:        {total_geral - 429:+d}")
