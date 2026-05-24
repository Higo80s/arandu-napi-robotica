"""
Análise detalhada: Comparação com números oficiais CAPES
"""

from app import app, db
from models import Bolsista, Modalidade, Edital

with app.app_context():
    print("=== COMPARACAO COM DADOS OFICIAIS CAPES ===\n")
    
    # Dados oficiais
    oficial_total = 429
    oficial_m_ppg = 255
    oficial_d_ppg = 151
    oficial_m_ies = 14
    oficial_d_ies = 9
    
    print("DADOS OFICIAIS CAPES:")
    print(f"  Total: {oficial_total}")
    print(f"  Mestrado PPG: {oficial_m_ppg}")
    print(f"  Doutorado PPG: {oficial_d_ppg}")
    print(f"  Mestrado IES: {oficial_m_ies}")
    print(f"  Doutorado IES: {oficial_d_ies}")
    
    # Dados do sistema
    print("\n=== DADOS DO SISTEMA ===\n")
    
    total_ativos = Bolsista.query.filter_by(ativo=True).count()
    print(f"Total bolsistas ATIVOS: {total_ativos}")
    
    # Por nível
    mestrado = Bolsista.query.join(Modalidade).filter(
        Bolsista.ativo==True,
        Modalidade.nivel.ilike('%mestrado%')
    ).count()
    
    doutorado = Bolsista.query.join(Modalidade).filter(
        Bolsista.ativo==True,
        Modalidade.nivel.ilike('%doutorado%')
    ).count()
    
    print(f"  Mestrado: {mestrado}")
    print(f"  Doutorado: {doutorado}")
    
    # Por edital (CAPES DS vs CAPES IES)
    print("\n=== POR EDITAL ===\n")
    
    editais = Edital.query.all()
    for edital in editais:
        bolsistas = Bolsista.query.filter_by(edital_id=edital.id, ativo=True).count()
        if bolsistas > 0:
            print(f"{edital.numero:30s} ({edital.agencia:10s}): {bolsistas:3d} bolsistas")
    
    # Edital 14 (CAPES DS - PPG)
    edital_ds = Edital.query.filter_by(numero='Edital 14/2024 - CAPES DS').first()
    if edital_ds:
        ds_total = Bolsista.query.filter_by(edital_id=edital_ds.id, ativo=True).count()
        ds_m = Bolsista.query.join(Modalidade).filter(
            Bolsista.edital_id==edital_ds.id,
            Bolsista.ativo==True,
            Modalidade.nivel.ilike('%mestrado%')
        ).count()
        ds_d = Bolsista.query.join(Modalidade).filter(
            Bolsista.edital_id==edital_ds.id,
            Bolsista.ativo==True,
            Modalidade.nivel.ilike('%doutorado%')
        ).count()
        
        print(f"\nCAPES DS (Edital 14):")
        print(f"  Total: {ds_total} (Oficial: {oficial_m_ppg + oficial_d_ppg} = 406)")
        print(f"  Mestrado: {ds_m} (Oficial: {oficial_m_ppg})")
        print(f"  Doutorado: {ds_d} (Oficial: {oficial_d_ppg})")
    
    # Edital 13 (CAPES IES)
    edital_ies = Edital.query.filter_by(numero='Edital 13/2024 - CAPES IES').first()
    if edital_ies:
        ies_total = Bolsista.query.filter_by(edital_id=edital_ies.id, ativo=True).count()
        ies_m = Bolsista.query.join(Modalidade).filter(
            Bolsista.edital_id==edital_ies.id,
            Bolsista.ativo==True,
            Modalidade.nivel.ilike('%mestrado%')
        ).count()
        ies_d = Bolsista.query.join(Modalidade).filter(
            Bolsista.edital_id==edital_ies.id,
            Bolsista.ativo==True,
            Modalidade.nivel.ilike('%doutorado%')
        ).count()
        
        print(f"\nCAPES IES (Edital 13):")
        print(f"  Total: {ies_total} (Oficial: {oficial_m_ies + oficial_d_ies} = 23)")
        print(f"  Mestrado: {ies_m} (Oficial: {oficial_m_ies})")
        print(f"  Doutorado: {ies_d} (Oficial: {oficial_d_ies})")
    
    # Discrepância
    print("\n=== ANALISE DE DISCREPANCIA ===\n")
    
    diff_total = total_ativos - oficial_total
    print(f"Diferença total: {diff_total:+d}")
    
    if diff_total > 0:
        print(f"\n⚠️  Sistema tem {diff_total} bolsistas A MAIS que o oficial")
        print("Possíveis causas:")
        print("  - Bolsistas de outros editais (Recursos Próprios, etc)")
        print("  - Bolsistas cadastrados mas não enviados para CAPES")
        print("  - Duplicatas não detectadas")
    elif diff_total < 0:
        print(f"\n⚠️  Sistema tem {abs(diff_total)} bolsistas A MENOS que o oficial")
        print("Possíveis causas:")
        print("  - Bolsistas da CAPES não cadastrados no sistema")
        print("  - Bolsistas marcados como inativos incorretamente")
    else:
        print("✅ Números batem perfeitamente!")
    
    # Bolsistas não-CAPES
    bolsistas_outros = Bolsista.query.filter(
        Bolsista.ativo==True,
        Bolsista.edital_id.notin_([edital_ds.id if edital_ds else 0, edital_ies.id if edital_ies else 0])
    ).count()
    
    print(f"\nBolsistas de OUTROS editais (não-CAPES): {bolsistas_outros}")
