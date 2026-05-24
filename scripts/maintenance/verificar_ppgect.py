"""
Verifica programa PPGECT Ponta Grossa
"""

from app import app, db
from models import ProgramaAcademico, Campus

with app.app_context():
    print("=== VERIFICANDO PPGECT PONTA GROSSA ===\n")
    
    # Buscar programa
    progs = ProgramaAcademico.query.filter(
        ProgramaAcademico.nome_programa.ilike('%ensino%ciência%tecnologia%')
    ).all()
    
    if not progs:
        progs = ProgramaAcademico.query.filter(
            ProgramaAcademico.nome_programa.ilike('%ensino%ciencia%tecnologia%')
        ).all()
    
    print(f"✅ Programas encontrados: {len(progs)}\n")
    
    for p in progs:
        print(f"ID: {p.id}")
        print(f"Nome: {p.nome_programa}")
        print(f"Sigla: {p.sigla_programa}")
        print(f"Código: {p.codigo_programa}")
        print(f"Campus: {p.campus.nome if p.campus else 'SEM CAMPUS'}")
        print(f"Campus ID: {p.campus_id}")
        print("-" * 60)
    
    # Verificar Campus PG
    print("\n=== CAMPUS PG ===")
    pg = Campus.query.filter_by(sigla_campus='PG').first()
    if pg:
        print(f"ID: {pg.id}")
        print(f"Nome: {pg.nome}")
        print(f"Sigla: {pg.sigla_campus}")
    else:
        print("❌ Campus PG não encontrado!")
    
    # Listar todos os programas de PG
    print("\n=== TODOS OS PROGRAMAS DE PONTA GROSSA ===")
    if pg:
        progs_pg = ProgramaAcademico.query.filter_by(campus_id=pg.id).all()
        print(f"Total: {len(progs_pg)}\n")
        for p in progs_pg:
            print(f"- {p.sigla_programa}: {p.nome_programa}")
