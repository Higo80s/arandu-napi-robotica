"""
Corrige programas profissionais para aparecerem em busca genérica
Atualiza MP → M,MP e DP → D,DP
"""

from app import app, db
from models import ProgramaAcademico

with app.app_context():
    print("=== CORRIGINDO PROGRAMAS PROFISSIONAIS ===\n")
    
    # Buscar todos com apenas MP ou DP
    programas_mp = ProgramaAcademico.query.filter_by(niveis="MP").all()
    programas_dp = ProgramaAcademico.query.filter_by(niveis="DP").all()
    
    print(f"Programas apenas MP: {len(programas_mp)}")
    print(f"Programas apenas DP: {len(programas_dp)}\n")
    
    # Corrigir MP → M,MP
    for p in programas_mp:
        print(f"ID {p.id:3d}: {p.sigla_programa:12s} | {p.nome_programa:45s}")
        print(f"       MP → M,MP ({p.campus.nome if p.campus else 'SEM CAMPUS'})")
        p.niveis = "M,MP"
    
    # Corrigir DP → D,DP  
    for p in programas_dp:
        print(f"ID {p.id:3d}: {p.sigla_programa:12s} | {p.nome_programa:45s}")
        print(f"       DP → D,DP ({p.campus.nome if p.campus else 'SEM CAMPUS'})")
        p.niveis = "D,DP"
    
    total = len(programas_mp) + len(programas_dp)
    
    if total > 0:
        db.session.commit()
        print(f"\n✅ {total} programas profissionais corrigidos!")
        print("\nAgora aparecem em buscas:")
        print("  - M,MP: Modalidade 'Mestrado' E 'Mestrado Profissional'")
        print("  - D,DP: Modalidade 'Doutorado' E 'Doutorado Profissional'")
    else:
        print("✅ Nenhuma correção necessária!")
