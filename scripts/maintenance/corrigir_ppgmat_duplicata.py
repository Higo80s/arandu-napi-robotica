"""
Script 2: Corrigir PPGMAT duplicado
Consolida 2 registros de ENSINO DE MATEMÁTICA (40006018041P3)
"""

from app import app, db
from models import ProgramaAcademico, Bolsista

with app.app_context():
    print("=== CORRIGINDO PPGMAT DUPLICADO ===\n")
    
    # Buscar duplicatas
    programas = ProgramaAcademico.query.filter_by(codigo_programa='40006018041P3').all()
    
    print(f"Encontrados: {len(programas)} registros\n")
    
    if len(programas) > 1:
        # Identificar qual manter (com mais bolsistas ou ID menor)
        programas_info = []
        for p in programas:
            count = Bolsista.query.filter_by(programa_id=p.id, ativo=True).count()
            programas_info.append((p, count))
            print(f"ID {p.id}: {p.nome_programa}")
            print(f"  Campus: {p.campus.nome if p.campus else 'SEM CAMPUS'}")
            print(f"  Bolsistas: {count}")
            print(f"  Niveis: {p.niveis}\n")
        
        # Manter o com mais bolsistas
        programas_info.sort(key=lambda x: (-x[1], x[0].id))
        manter = programas_info[0][0]
        excluir = [p[0] for p in programas_info[1:]]
        
        print(f"DECISAO:")
        print(f"  Manter: ID {manter.id} ({programas_info[0][1]} bolsistas)")
        print(f"  Excluir: {[p.id for p in excluir]}\n")
        
        # Transferir bolsistas
        for prog in excluir:
            bolsistas = Bolsista.query.filter_by(programa_id=prog.id).all()
            
            for b in bolsistas:
                print(f"  Transferindo: {b.nome} → ID {manter.id}")
                b.programa_id = manter.id
                b.programa = manter.nome_programa
                if manter.campus:
                    b.campus = manter.campus.nome
                    b.campus_sigla = manter.campus.sigla_campus
            
            # Excluir programa duplicado
            print(f"\n  Excluindo programa ID {prog.id}...")
            db.session.delete(prog)
        
        db.session.commit()
        print("\n✅ Correcao concluida!")
        
    else:
        print("✅ Apenas 1 registro encontrado - OK!")
