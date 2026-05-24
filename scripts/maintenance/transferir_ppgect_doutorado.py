"""
Transfere bolsistas de Doutorado PPGECT restantes para ID 130
"""

from app import app, db
from models import Bolsista, ProgramaAcademico

with app.app_context():
    print("=== TRANSFERINDO BOLSISTAS DOUTORADO PPGECT ===\n")
    
    # Buscar programa Mestrado (ID 42)
    ppgect_mestrado = ProgramaAcademico.query.get(42)
    
    if not ppgect_mestrado:
        print("❌ Programa ID 42 não encontrado!")
        exit(1)
    
    # Buscar bolsistas de Doutorado vinculados ao Mestrado
    bolsistas_42 = Bolsista.query.filter_by(programa_id=42).all()
    
    transferidos = []
    
    for b in bolsistas_42:
        if not b.modalidade:
            continue
        
        nivel = b.modalidade.nivel.upper()
        
        if 'DOUTORADO' in nivel or 'D' == nivel or 'DOCTOR' in nivel:
            print(f"Transferindo: {b.nome}")
            print(f"  Nivel: {b.modalidade.nivel}")
            print(f"  De: ID 42 (Mestrado) → Para: ID 130 (Doutorado)")
            
            b.programa_id = 130
            transferidos.append(b.nome)
    
    if transferidos:
        db.session.commit()
        print(f"\n✅ {len(transferidos)} bolsistas transferidos!")
        print("\nLista:")
        for nome in transferidos:
            print(f"  - {nome}")
    else:
        print("✅ Nenhum bolsista de Doutorado encontrado no ID 42")
    
    # Verificar resultado
    print("\n=== RESULTADO FINAL ===\n")
    
    bolsistas_m = Bolsista.query.filter_by(programa_id=42).count()
    bolsistas_d = Bolsista.query.filter_by(programa_id=130).count()
    
    print(f"PPGECT Mestrado (ID 42): {bolsistas_m} bolsistas")
    print(f"PPGECT Doutorado (ID 130): {bolsistas_d} bolsistas")
