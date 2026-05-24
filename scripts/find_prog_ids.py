import os
import sys

# Ensure project root is in path BEFORE any local imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import app, db
from models import ProgramaAcademico

def find_programs():
    with app.app_context():
        print("Buscando programas no banco...")
        # Check for typos or extra codes
        codes = ["4006018022P9", "40006018022P9", "40006018028P7"]
        for c in codes:
            p = ProgramaAcademico.query.filter_by(codigo_programa=c).first()
            if p:
                print(f"ID: {p.id} | Código: {p.codigo_programa} | Nome: {p.nome_programa}")
            else:
                print(f"Código {c} não encontrado")

if __name__ == "__main__":
    find_programs()
