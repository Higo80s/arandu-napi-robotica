import sys
import os

# Contexto da Aplicação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import ProgramaAcademico

def run():
    with app.app_context():
        # Code from user table: 33004013069P2
        code = '33004013069P2'
        prog = ProgramaAcademico.query.filter_by(codigo_programa=code).first()
        
        if prog:
            print(f"Found by CODE: {prog.sigla_programa} | {prog.nome_programa} | ID: {prog.id}")
        else:
            print(f"Not found by CODE: {code}")
            
        # Try without the 'P2' suffix just in case
        code_short = '33004013069'
        prog2 = ProgramaAcademico.query.filter(ProgramaAcademico.codigo_programa.like(f"%{code_short}%")).first()
        if prog2:
             print(f"Found by PARTIAL CODE: {prog2.sigla_programa} | {prog2.nome_programa} | ID: {prog2.id}")

if __name__ == '__main__':
    run()
