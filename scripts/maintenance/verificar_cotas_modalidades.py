"""
Verifica cotas CAPES cadastradas na tabela Modalidade
"""

from app import app
from models import Modalidade, Edital

with app.app_context():
    print("=== COTAS CAPES CADASTRADAS ===\n")
    
    # Buscar editais CAPES
    edital_ds = Edital.query.filter(
        (Edital.numero.ilike('%edital 14%')) | 
        (Edital.numero.ilike('%capes ds%'))
    ).first()
    
    edital_ies = Edital.query.filter(
        (Edital.numero.ilike('%edital 13%')) | 
        (Edital.numero.ilike('%capes ies%'))
    ).first()
    
    if edital_ds:
        print(f"CAPES DS: {edital_ds.numero}\n")
        
        modalidades_ds = Modalidade.query.filter_by(edital_id=edital_ds.id).all()
        
        total_m_ds = 0
        total_d_ds = 0
        
        print("Modalidades cadastradas:")
        for m in modalidades_ds:
            nivel_clean = m.nivel.upper()
            vagas = m.vagas or 0
            
            if 'MESTRADO' in nivel_clean:
                total_m_ds += vagas
                print(f"  Mestrado: {vagas} vagas")
            elif 'DOUTORADO' in nivel_clean:
                total_d_ds += vagas
                print(f"  Doutorado: {vagas} vagas")
        
        print(f"\nTotal CAPES DS:")
        print(f"  Mestrado:  {total_m_ds} (Esperado: 255)")
        print(f"  Doutorado: {total_d_ds} (Esperado: 151)")
        print(f"  Total:     {total_m_ds + total_d_ds} (Esperado: 406)")
    
    if edital_ies:
        print(f"\n\nCAPES IES: {edital_ies.numero}\n")
        
        modalidades_ies = Modalidade.query.filter_by(edital_id=edital_ies.id).all()
        
        total_m_ies = 0
        total_d_ies = 0
        
        print("Modalidades cadastradas:")
        for m in modalidades_ies:
            nivel_clean = m.nivel.upper()
            vagas = m.vagas or 0
            
            if 'MESTRADO' in nivel_clean:
                total_m_ies += vagas
                print(f"  Mestrado: {vagas} vagas")
            elif 'DOUTORADO' in nivel_clean:
                total_d_ies += vagas
                print(f"  Doutorado: {vagas} vagas")
        
        print(f"\nTotal CAPES IES:")
        print(f"  Mestrado:  {total_m_ies} (Esperado: 14)")
        print(f"  Doutorado: {total_d_ies} (Esperado: 9)")
        print(f"  Total:     {total_m_ies + total_d_ies} (Esperado: 23)")
    
    # Total geral
    if edital_ds and edital_ies:
        total_capes = total_m_ds + total_d_ds + total_m_ies + total_d_ies
        print(f"\n\nTOTAL GERAL CAPES:")
        print(f"  {total_capes} cotas (Esperado: 429)")
        
        diff = total_capes - 429
        if diff != 0:
            print(f"  Diferenca: {diff:+d}")
