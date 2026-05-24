"""
Verifica e corrige dados do PPGECT conforme Sucupira
"""

from app import app, db
from models import ProgramaAcademico, Campus

with app.app_context():
    print("=== VERIFICANDO PPGECT ATUAL ===\n")
    
    ppgects = ProgramaAcademico.query.filter_by(sigla_programa='PPGECT').all()
    
    for p in ppgects:
        print(f"ID: {p.id}")
        print(f"Nome: {p.nome_programa}")
        print(f"Código: {p.codigo_programa}")
        print(f"Sigla: {p.sigla_programa}")
        print(f"Campus: {p.campus.nome if p.campus else 'SEM CAMPUS'}")
        print("-" * 60)
    
    print("\n=== DADOS CORRETOS (SUCUPIRA) ===\n")
    print("40006018006P3 - ENSINO DE CIENCIA E TECNOLOGIA - PPGECT - PG - Mestrado Profissional")
    print("40006018028P7 - ENSINO DE CIENCIA E TECNOLOGIA - PPGECT - PG - Doutorado Academico")
    
    print("\n=== ACAO NECESSARIA ===\n")
    
    # Buscar Campus PG
    pg = Campus.query.filter_by(sigla_campus='PG').first()
    
    if len(ppgects) == 1:
        # Há apenas 1 registro, mas precisam ser 2
        print("PROBLEMA: Existe apenas 1 registro PPGECT, mas devem ser 2 (M e D)")
        print("\nSOLUCAO: Atualizar o existente e criar o segundo")
        
        ppgect_atual = ppgects[0]
        
        # Atualizar o existente para Mestrado
        print(f"\n1. Atualizando ID {ppgect_atual.id} para Mestrado:")
        ppgect_atual.codigo_programa = "40006018006P3"
        ppgect_atual.nome_programa = "ENSINO DE CIENCIA E TECNOLOGIA (MESTRADO)"
        
        # Criar novo para Doutorado
        print("2. Criando registro para Doutorado:")
        ppgect_doutorado = ProgramaAcademico(
            nome_programa="ENSINO DE CIENCIA E TECNOLOGIA (DOUTORADO)",
            sigla_programa="PPGECT",
            codigo_programa="40006018028P7",
            campus_id=pg.id
        )
        db.session.add(ppgect_doutorado)
        
        db.session.commit()
        
        print("\n✅ CORRIGIDO!")
        print(f"   - ID {ppgect_atual.id}: Mestrado (40006018006P3)")
        print(f"   - ID {ppgect_doutorado.id}: Doutorado (40006018028P7)")
        
    elif len(ppgects) >= 2:
        print("ENCONTRADOS 2+ registros PPGECT")
        print("\nVerificando códigos...")
        
        tem_mestrado = any(p.codigo_programa == "40006018006P3" for p in ppgects)
        tem_doutorado = any(p.codigo_programa == "40006018028P7" for p in ppgects)
        
        if tem_mestrado and tem_doutorado:
            print("✅ CORRETO! Ambos os códigos já estão cadastrados")
        else:
            print("❌ CÓDIGOS INCORRETOS! Corrigindo...")
            
            # Atualizar primeiros 2 registros
            ppgects[0].codigo_programa = "40006018006P3"
            ppgects[0].nome_programa = "ENSINO DE CIENCIA E TECNOLOGIA (MESTRADO)"
            
            ppgects[1].codigo_programa = "40006018028P7"
            ppgects[1].nome_programa = "ENSINO DE CIENCIA E TECNOLOGIA (DOUTORADO)"
            
            # Remover extras se houver
            if len(ppgects) > 2:
                print(f"\nRemovendo {len(ppgects) - 2} registros extras...")
                for p in ppgects[2:]:
                    db.session.delete(p)
            
            db.session.commit()
            print("✅ CORRIGIDO!")
    
    else:
        print("❌ NENHUM PPGECT ENCONTRADO! Criando os 2 registros...")
        
        # Criar Mestrado
        ppgect_m = ProgramaAcademico(
            nome_programa="ENSINO DE CIENCIA E TECNOLOGIA (MESTRADO)",
            sigla_programa="PPGECT",
            codigo_programa="40006018006P3",
            campus_id=pg.id
        )
        
        # Criar Doutorado
        ppgect_d = ProgramaAcademico(
            nome_programa="ENSINO DE CIENCIA E TECNOLOGIA (DOUTORADO)",
            sigla_programa="PPGECT",
            codigo_programa="40006018028P7",
            campus_id=pg.id
        )
        
        db.session.add(ppgect_m)
        db.session.add(ppgect_d)
        db.session.commit()
        
        print("✅ CRIADOS!")
    
    # Verificar resultado final
    print("\n=== RESULTADO FINAL ===\n")
    ppgects_final = ProgramaAcademico.query.filter_by(sigla_programa='PPGECT').all()
    for p in ppgects_final:
        print(f"ID {p.id}: {p.codigo_programa} - {p.nome_programa}")
