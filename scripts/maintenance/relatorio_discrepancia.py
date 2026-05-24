"""
Relatório detalhado de discrepância CAPES
"""

from app import app, db
from models import Bolsista, Modalidade, Edital
from sqlalchemy import func

with app.app_context():
    print("=== ANALISE DE DISCREPANCIA CAPES ===\n")
    
    # 1. Total geral
    total_sistema = Bolsista.query.filter_by(ativo=True).count()
    total_oficial = 429
    
    print(f"Sistema:  {total_sistema} bolsistas ativos")
    print(f"Oficial:  {total_oficial} bolsistas CAPES")
    print(f"Diferenca: {total_sistema - total_oficial:+d}\n")
    
    # 2. Por edital
    print("=== BOLSISTAS POR EDITAL ===\n")
    
    editais_resumo = db.session.query(
        Edital.numero,
        Edital.agencia,
        func.count(Bolsista.id).filter(Bolsista.ativo == True).label('total')
    ).outerjoin(Bolsista).group_by(Edital.id).all()
    
    capes_ds = 0
    capes_ies = 0
    outros = 0
    
    for numero, agencia, total in editais_resumo:
        if total > 0:
            print(f"{numero[:35]:35s} | {agencia[:10]:10s} | {total:3d}")
            
            if 'Edital 14' in numero or 'CAPES DS' in numero:
                capes_ds = total
            elif 'Edital 13' in numero or 'CAPES IES' in numero:
                capes_ies = total
            else:
                outros += total
    
    print(f"\nRESUMO:")
    print(f"  CAPES DS (PPG):  {capes_ds}")
    print(f"  CAPES IES:       {capes_ies}")
    print(f"  Outros editais:  {outros}")
    print(f"  Total:           {capes_ds + capes_ies + outros}")
    
    # 3. Comparação esperada
    print(f"\n=== COMPARACAO ===\n")
    print(f"SISTEMA:")
    print(f"  CAPES DS:  {capes_ds} (Esperado: 406 = 255M + 151D)")
    print(f"  CAPES IES: {capes_ies} (Esperado: 23 = 14M + 9D)")
    print(f"  Total CAPES: {capes_ds + capes_ies} (Esperado: 429)")
    print(f"  Outros: {outros}")
    
    print(f"\nDIFERENCAS:")
    diff_ds = capes_ds - 406
    diff_ies = capes_ies - 23
    print(f"  CAPES DS:  {diff_ds:+d}")
    print(f"  CAPES IES: {diff_ies:+d}")
    
    # 4. Conclusão
    print(f"\n=== CONCLUSAO ===\n")
    if outros > 0:
        print(f"O sistema tem {outros} bolsistas de OUTROS editais (Recursos Proprios, etc)")
        print(f"Esses NAO devem ser contabilizados na comparacao com CAPES")
        print(f"\nTotal APENAS CAPES: {capes_ds + capes_ies}")
        diff_real = (capes_ds + capes_ies) - total_oficial
        if diff_real == 0:
            print(f"✅ Numeros batem PERFEITAMENTE com CAPES!")
        else:
            print(f"⚠️  Diferenca real: {diff_real:+d}")
