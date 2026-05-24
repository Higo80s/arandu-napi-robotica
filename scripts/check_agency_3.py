import sys
import os
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import AgenciaFomento

def run():
    with app.app_context():
        a = AgenciaFomento.query.get(3)
        if a:
            print(f"ID: {a.id}")
            print(f"Sigla: '{a.sigla}'")
            print(f"Nome: '{a.nome}'")
        else:
            print("Agency 3 not found")

if __name__ == '__main__':
    run()
