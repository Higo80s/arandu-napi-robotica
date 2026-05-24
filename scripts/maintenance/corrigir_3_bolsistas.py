"""
Verifica e corrige PPGFCET e PPGPGP
Depois atualiza os 3 bolsistas
"""

from app import app, db
from models import ProgramaAcademico, Bolsista

with app.app_context():
    print("=== VERIFICANDO PROGRAMAS ===\n")
    
    # 1. PPGFCET
    ppgfcet = ProgramaAcademico.query.filter_by(codigo_programa='40006018019P8').first()
    
    if ppgfcet:
        print(f"✅ PPGFCET encontrado:")
        print(f"   ID: {ppgfcet.id}")
        print(f"   Nome: {ppgfcet.nome_programa}")
        print(f"   Campus: {ppgfcet.campus.nome if ppgfcet.campus else 'SEM CAMPUS'}")
        print(f"   Níveis: '{ppgfcet.niveis}'")
        
        if not ppgfcet.niveis or ppgfcet.niveis == 'None':
            print("   ⚠️  Campo niveis VAZIO - CORRIGINDO...")
            ppgfcet.niveis = 'MP,DP'
            db.session.commit()
            print("   ✅ Corrigido para: MP,DP")
    else:
        print("❌ PPGFCET NÃO ENCONTRADO!")
    
    print()
    
    # 2. PPGPGP
    ppgpgp = ProgramaAcademico.query.filter_by(codigo_programa='40006018017P5').first()
    
    if ppgpgp:
        print(f"✅ PPGPGP encontrado:")
        print(f"   ID: {ppgpgp.id}")
        print(f"   Nome: {ppgpgp.nome_programa}")
        print(f"   Campus: {ppgpgp.campus.nome if ppgpgp.campus else 'SEM CAMPUS'}")
        print(f"   Níveis: '{ppgpgp.niveis}'")
        
        if not ppgpgp.niveis or ppgpgp.niveis == 'None':
            print("   ⚠️  Campo niveis VAZIO - CORRIGINDO...")
            ppgpgp.niveis = 'MP,DP'
            db.session.commit()
            print("   ✅ Corrigido para: MP,DP")
    else:
        print("❌ PPGPGP NÃO ENCONTRADO!")
    
    print("\n" + "=" * 70)
    print("ATUALIZANDO OS 3 BOLSISTAS")
    print("=" * 70 + "\n")
    
    # Bolsista 570 - PPGFCET
    b570 = Bolsista.query.get(570)
    if b570 and ppgfcet:
        print(f"Bolsista 570: {b570.nome}")
        print(f"  Programa atual: {b570.programa or 'VAZIO'}")
        print(f"  Atualizando para: PPGFCET (ID {ppgfcet.id})")
        
        b570.programa_id = ppgfcet.id
        b570.programa = ppgfcet.nome_programa
        b570.campus = ppgfcet.campus.nome if ppgfcet.campus else None
        b570.campus_sigla = ppgfcet.campus.sigla_campus if ppgfcet.campus else None
        db.session.commit()
        print("  ✅ Atualizado!\n")
    
    # Bolsista 558 - PPGFCET
    b558 = Bolsista.query.get(558)
    if b558 and ppgfcet:
        print(f"Bolsista 558: {b558.nome}")
        print(f"  Programa atual: {b558.programa or 'VAZIO'}")
        print(f"  Atualizando para: PPGFCET (ID {ppgfcet.id})")
        
        b558.programa_id = ppgfcet.id
        b558.programa = ppgfcet.nome_programa
        b558.campus = ppgfcet.campus.nome if ppgfcet.campus else None
        b558.campus_sigla = ppgfcet.campus.sigla_campus if ppgfcet.campus else None
        db.session.commit()
        print("  ✅ Atualizado!\n")
    
    # Bolsista 559 - PPGPGP
    b559 = Bolsista.query.get(559)
    if b559 and ppgpgp:
        print(f"Bolsista 559: {b559.nome}")
        print(f"  Programa atual: {b559.programa or 'VAZIO'}")
        print(f"  Atualizando para: PPGPGP (ID {ppgpgp.id})")
        
        b559.programa_id = ppgpgp.id
        b559.programa = ppgpgp.nome_programa
        b559.campus = ppgpgp.campus.nome if ppgpgp.campus else None
        b559.campus_sigla = ppgpgp.campus.sigla_campus if ppgpgp.campus else None
        db.session.commit()
        print("  ✅ Atualizado!\n")
    
    print("=" * 70)
    print("✅ CORREÇÕES CONCLUÍDAS!")
    print("=" * 70)
