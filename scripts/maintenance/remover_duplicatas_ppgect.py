"""
Remove duplicatas do PPGECT
Mantém apenas ID 42 (original)
"""

from app import app, db
from models import ProgramaAcademico, Bolsista

with app.app_context():
    print("=== REMOVENDO DUPLICATAS PPGECT ===\n")
    
    # Verificar se há bolsistas vinculados aos IDs duplicados
    print("Verificando bolsistas vinculados...\n")
    
    for prog_id in [67, 126]:
        bolsistas = Bolsista.query.filter_by(programa_id=prog_id).all()
        print(f"PPGECT ID {prog_id}: {len(bolsistas)} bolsistas vinculados")
        
        if bolsistas:
            print(f"  Transferindo {len(bolsistas)} bolsistas para ID 42...")
            for b in bolsistas:
                b.programa_id = 42
            db.session.commit()
            print(f"  Transferido!")
    
    # Deletar duplicatas
    print("\nRemovendo duplicatas...")
    ProgramaAcademico.query.filter(ProgramaAcademico.id.in_([67, 126])).delete(synchronize_session=False)
    db.session.commit()
    
    print("✅ Duplicatas removidas!\n")
    
    # Verificar resultado
    ppgects = ProgramaAcademico.query.filter_by(sigla_programa='PPGECT').all()
    print(f"PPGECT restantes: {len(ppgects)}")
    for p in ppgects:
        bolsistas_count = Bolsista.query.filter_by(programa_id=p.id).count()
        print(f"  ID {p.id}: {p.nome_programa} - {bolsistas_count} bolsistas")
