import sys
import os
from sqlalchemy import text

# Contexto da Aplicação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import ProgramaAcademico

def run():
    print("--- PROGRAM LEVELS ANALYSIS ---")
    with app.app_context():
        # Count by niveis
        results = db.session.query(ProgramaAcademico.niveis, db.func.count(ProgramaAcademico.id))\
            .group_by(ProgramaAcademico.niveis).all()
        
        print(f"{'Niveis':<20} | {'Count':<10}")
        print("-" * 35)
        for nivel, count in results:
            print(f"{str(nivel):<20} | {count:<10}")

if __name__ == '__main__':
    run()
