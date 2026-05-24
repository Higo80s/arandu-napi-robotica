"""
Verifica totais REAIS de bolsistas CAPES DS e IES no banco
"""

from app import app
from models import Bolsista, Modalidade, Edital

with app.app_context():
    print("=== VERIFICACAO BOLSISTAS CAPES ===\n")
    
    # Buscar editais CAPES
    edital_ds = Edital.query.filter(
        (Edital.numero.ilike('%edital 14%')) | 
        (Edital.numero.ilike('%capes ds%'))
    ).first()
    
    edital_ies = Edital.query.filter(
        (Edital.numero.ilike('%edital 13%')) | 
        (Edital.numero.ilike('%capes ies%'))
    ).first()
    
    print(f"Edital DS encontrado: {edital_ds.numero if edital_ds else 'NAO ENCONTRADO'}")
    print(f"Edital IES encontrado: {edital_ies.numero if edital_ies else 'NAO ENCONTRADO'}")
    print()
    
    if edital_ds:
        # CAPES DS - Totais
        ds_total = Bolsista.query.filter_by(edital_id=edital_ds.id, ativo=True).count()
        
        ds_mestrado = Bolsista.query.join(Modalidade).filter(
            Bolsista.edital_id == edital_ds.id,
            Bolsista.ativo == True,
            Modalidade.nivel.ilike('%mestrado%')
        ).count()
        
        ds_doutorado = Bolsista.query.join(Modalidade).filter(
            Bolsista.edital_id == edital_ds.id,
            Bolsista.ativo == True,
            Modalidade.nivel.ilike('%doutorado%')
        ).count()
        
        print("CAPES DS (Edital 14) - PPG Sucupira:")
        print(f"  Mestrado: {ds_mestrado} (Esperado: 255)")
        print(f"  Doutorado: {ds_doutorado} (Esperado: 151)")
        print(f"  Total: {ds_total} (Esperado: 406)")
        print()
    
    if edital_ies:
        # CAPES IES - Totais
        ies_total = Bolsista.query.filter_by(edital_id=edital_ies.id, ativo=True).count()
        
        ies_mestrado = Bolsista.query.join(Modalidade).filter(
            Bolsista.edital_id == edital_ies.id,
            Bolsista.ativo == True,
            Modalidade.nivel.ilike('%mestrado%')
        ).count()
        
        ies_doutorado = Bolsista.query.join(Modalidade).filter(
            Bolsista.edital_id == edital_ies.id,
            Bolsista.ativo == True,
            Modalidade.nivel.ilike('%doutorado%')
        ).count()
        
        print("CAPES IES (Edital 13) - IES Participante:")
        print(f"  Mestrado: {ies_mestrado} (Esperado: 14)")
        print(f"  Doutorado: {ies_doutorado} (Esperado: 9)")
        print(f"  Total: {ies_total} (Esperado: 23)")
        print()
    
    # Total CAPES
    if edital_ds and edital_ies:
        total_capes = ds_total + ies_total
        print(f"TOTAL CAPES: {total_capes} (Esperado: 429)")
        
        diff = total_capes - 429
        if diff != 0:
            print(f"\nDIFERENCTA: {diff:+d}")
            if diff > 0:
                print("  Sistema tem bolsistas A MAIS")
            else:
                print("  Sistema tem bolsistas A MENOS")
