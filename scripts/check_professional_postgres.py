import sys
import os
import logging
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import ProgramaAcademico, Campus

def check_professional_programs():
    print("Connecting to PostgreSQL...")
    with app.app_context():
        # Query all programs with tipo_oferta='Profissional'
        profs = db.session.query(ProgramaAcademico, Campus)\
            .join(Campus, ProgramaAcademico.campus_id == Campus.id)\
            .filter(ProgramaAcademico.tipo_oferta == 'Profissional')\
            .order_by(ProgramaAcademico.nome_programa).all()
        
        print(f"Found {len(profs)} Professional Programs:")
        print(f"{'Code':<15} | {'Sigla':<10} | {'Campus':<5} | {'Name'}")
        print("-" * 60)
        
        for p, c in profs:
            print(f"{p.codigo_programa:<15} | {p.sigla_programa:<10} | {c.sigla_campus:<5} | {p.nome_programa}")

if __name__ == "__main__":
    if 'postgresql' not in app.config['SQLALCHEMY_DATABASE_URI']:
        print("WARNING: Not connected to PostgreSQL!")
    else:
        check_professional_programs()
