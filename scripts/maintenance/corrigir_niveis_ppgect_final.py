"""
Corrige niveis do PPGECT para aceitar M e MP
"""

from app import app, db
from models import ProgramaAcademico

with app.app_context():
    print("=== CORRIGINDO NIVEIS PPGECT ===\n")
    
    # ID 42: Mestrado - Deve aceitar M e MP
    ppgect_m = ProgramaAcademico.query.get(42)
    if ppgect_m:
        print(f"ID 42 - PPGECT Mestrado")
        print(f"  Niveis ANTES: {ppgect_m.niveis}")
        ppgect_m.niveis = "M,MP"  # Aceita AMBOS: Mestrado Acadêmico E Profissional
        print(f"  Niveis DEPOIS: M,MP")
        print(f"  ✅ Agora aceita Mestrado Acadêmico E Profissional")
    
    # ID 130: Doutorado - Já está correto com D
    ppgect_d = ProgramaAcademico.query.get(130)
    if ppgect_d:
        print(f"\nID 130 - PPGECT Doutorado")
        print(f"  Niveis ATUAL: {ppgect_d.niveis}")
        print(f"  ✅ Já está correto (D = Doutorado Acadêmico)")
    
    db.session.commit()
    print("\n✅ Correção aplicada!")
    
    print("\n=== VERIFICAÇÃO ===")
    print("\nAgora o PPGECT Mestrado irá aparecer para:")
    print("  - Bolsistas com modalidade 'Mestrado' (M)")
    print("  - Bolsistas com modalidade 'Mestrado Profissional' (MP)")
