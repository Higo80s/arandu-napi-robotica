import sys
import os

# Contexto da Aplicação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import ProgramaAcademico

def run():
    with app.app_context():
        progs = ProgramaAcademico.query.filter(ProgramaAcademico.nome_programa.ilike('%agua%') | ProgramaAcademico.sigla_programa.ilike('%agua%')).all()
        for p in progs:
            print(f"{p.sigla_programa} | {p.nome_programa}")
            
        # Also try ProfiAGUA without searching string
        progs2 = ProgramaAcademico.query.filter(ProgramaAcademico.sigla_programa.ilike('%PROFI%')).all()
        for p in progs2:
             print(f"{p.sigla_programa} | {p.nome_programa}")

if __name__ == '__main__':
    run()
