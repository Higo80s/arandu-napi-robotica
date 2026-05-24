from app import app, db
from models import ProgramaAcademico, Bolsista, Residente
from sqlalchemy import func

with app.app_context():
    # 1. Find duplicate codes
    duplicates = db.session.query(
        ProgramaAcademico.codigo_programa,
        func.count(ProgramaAcademico.id)
    ).group_by(ProgramaAcademico.codigo_programa).having(func.count(ProgramaAcademico.id) > 1).all()

    with open('duplicates_report.txt', 'w', encoding='utf-8') as f:
        f.write(f"Found {len(duplicates)} duplicate codes.\n")

        for code, count in duplicates:
            f.write(f"\nCode: {code} (Count: {count})\n")
            progs = ProgramaAcademico.query.filter_by(codigo_programa=code).all()
            
            for p in progs:
                b_count = Bolsista.query.filter_by(programa_id=p.id).count()
                r_count = Residente.query.filter_by(programa_id=p.id).count()
                f.write(f"  - ID: {p.id}, Name: {p.nome_programa}, Sigla: {p.sigla_programa}, Campus: {p.campus.sigla_campus if p.campus else 'N/A'}\n")
                f.write(f"    Linked Records: Bolsistas={b_count}, Residentes={r_count}\n")

    # 2. Check current logic for admin_programas_lista (simulate query)
    # User asked for ordering. Let's see how current list looks.
    print("\n--- Current Listing Order (First 10) ---")
    all_progs = ProgramaAcademico.query.all() # No order specified by default?
    for p in all_progs[:10]:
        print(f"  {p.codigo_programa} - {p.nome_programa}")
