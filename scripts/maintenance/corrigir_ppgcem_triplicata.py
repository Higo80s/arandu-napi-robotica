"""
Script 3: Corrigir PPGCEM triplicado
Consolida 3 registros de CIÊNCIA E ENGENHARIA DE MATERIAIS (40006018175P0)
"""

from app import app, db
from models import ProgramaAcademico, Bolsista

with app.app_context():
    print("=== CORRIGINDO PPGCEM TRIPLICADO ===\n")
    
    # Buscar triplicatas
    programas = ProgramaAcademico.query.filter_by(codigo_programa='40006018175P0').all()
    
    print(f"Encontrados: {len(programas)} registros\n")
    
    if len(programas) > 1:
        # Listar todos
        programas_info = []
        for p in programas:
            count = Bolsista.query.filter_by(programa_id=p.id, ativo=True).count()
            campus_nome = p.campus.nome if p.campus else 'SEM CAMPUS'
            programas_info.append((p, count, campus_nome))
            print(f"ID {p.id}: {p.nome_programa}")
            print(f"  Campus: {campus_nome}")
            print(f"  Campus ID: {p.campus_id}")
            print(f"  Bolsistas: {count}")
            print(f"  Niveis: {p.niveis}\n")
        
        # Manter o com mais bolsistas OU primeiro campus alfabético
        programas_info.sort(key=lambda x: (-x[1], x[2], x[0].id))
        manter = programas_info[0][0]
        excluir = [p[0] for p in programas_info[1:]]
        
        print(f"DECISAO:")
        print(f"  Manter: ID {manter.id} - {programas_info[0][2]} ({programas_info[0][1]} bolsistas)")
        print(f"  Excluir: {[(p.id, p.campus.nome if p.campus else 'N/A') for p in excluir]}\n")
        
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
            
            # Excluir programa
            print(f"  Excluindo programa ID {prog.id}...")
            db.session.delete(prog)
        
        db.session.commit()
        print("\n✅ Correcao concluida!")
        
    else:
        print("✅ Apenas 1 registro - OK!")
