"""
Script 1: Verificar estado atual do sistema
Identifica as issues reportadas
"""

from app import app
from models import ProgramaAcademico, Bolsista

with app.app_context():
    print("=== VERIFICACAO DO SISTEMA ===\n")
    
    # 1. PPGPGP Duplicado
    print("1. PPGPGP - Verificando duplicatas:")
    ppgpgp_correto = ProgramaAcademico.query.filter_by(codigo_programa='40006018017P5').first()
    ppgpgp_dup = ProgramaAcademico.query.filter_by(codigo_programa='40006018012p7').first()
    
    if ppgpgp_correto and ppgpgp_dup:
        count_dup = Bolsista.query.filter_by(programa_id=ppgpgp_dup.id, ativo=True).count()
        print(f"  Correto (40006018017P5): ID {ppgpgp_correto.id}")
        print(f"  Duplicata (40006018012p7): ID {ppgpgp_dup.id} - {count_dup} bolsistas")
    else:
        print("  OK - Nao encontrada duplicata")
    
    # 2. PPGMAT Duplicado
    print("\n2. PPGMAT - Verificando duplicatas:")
    ppgmat_all = ProgramaAcademico.query.filter_by(codigo_programa='40006018041P3').all()
    print(f"  Encontrados: {len(ppgmat_all)} registros")
    for p in ppgmat_all:
        count = Bolsista.query.filter_by(programa_id=p.id, ativo=True).count()
        print(f"    ID {p.id}: {p.nome_programa} - {count} bolsistas")
    
    # 3. PPGCEM Triplicado
    print("\n3. PPGCEM - Verificando triplicacao:")
    ppgcem_all = ProgramaAcademico.query.filter_by(codigo_programa='40006018175P0').all()
    print(f"  Encontrados: {len(ppgcem_all)} registros")
    for p in ppgcem_all:
        campus = p.campus.nome if p.campus else 'SEM CAMPUS'
        count = Bolsista.query.filter_by(programa_id=p.id, ativo=True).count()
        print(f"    ID {p.id}: {campus} - {count} bolsistas")
    
    # 4. PPGFCET Ausente
    print("\n4. PPGFCET - Verificando existencia:")
    ppgfcet_all = ProgramaAcademico.query.filter_by(codigo_programa='40006018019P8').all()
    if ppgfcet_all:
        print(f"  Encontrados: {len(ppgfcet_all)} registros")
        for p in ppgfcet_all:
            print(f"    ID {p.id}: niveis={p.niveis} campus_id={p.campus_id}")
    else:
        print("  PROBLEMA: Programa nao encontrado no banco!")
    
    print("\n" + "="*60)
    print("RESUMO:")
    print(f"  PPGPGP: {'Duplicata encontrada' if ppgpgp_dup else 'OK'}")
    print(f"  PPGMAT: {len(ppgmat_all)} registros")
    print(f"  PPGCEM: {len(ppgcem_all)} registros")
    print(f"  PPGFCET: {'Encontrado' if ppgfcet_all else 'AUSENTE'}")
