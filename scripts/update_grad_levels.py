import sys
import os
import logging
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import ProgramaAcademico

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def update_grad_levels():
    print("--- Updating Graduation Course Levels to 'G' ---")
    with app.app_context():
        # Find programs with 'Graduacao' in name or level 'GRAD'
        candidates = ProgramaAcademico.query.filter(
            (ProgramaAcademico.nome_programa.ilike('%Gradua%')) |
            (ProgramaAcademico.niveis == 'GRAD')
        ).all()
        
        count = 0
        for p in candidates:
            print(f"Updating [{p.codigo_programa}] {p.nome_programa} -> 'G'")
            p.niveis = 'G'
            count += 1
            
        db.session.commit()
        print(f"Updated {count} programs.")

if __name__ == "__main__":
    update_grad_levels()
