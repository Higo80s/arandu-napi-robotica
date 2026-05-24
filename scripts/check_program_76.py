import sys
import os
from sqlalchemy import text

# Contexto da Aplicação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import ProgramaAcademico

def run():
    print("--- CHECK PROGRAM 76 ---")
    with app.app_context():
        p = ProgramaAcademico.query.get(76)
        if p:
            print(f"ID: {p.id}")
            print(f"Code: {p.codigo_programa}")
            print(f"Name: {p.nome_programa}")
            print(f"Campus ID: {p.campus_id}")
            print(f"Niveis: {p.niveis}")
        else:
            print("ID 76 not found in DB.")
            
        # Check if there is any '0' code
        p0 = ProgramaAcademico.query.filter_by(codigo_programa='0').first()
        if p0:
            print(f"Found Code '0': ID={p0.id} Name={p0.nome_programa}")
            
if __name__ == '__main__':
    run()
