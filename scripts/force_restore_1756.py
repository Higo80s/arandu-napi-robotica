import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Edital, Modalidade
from datetime import date

def force_1756():
    with app.app_context():
        print("Checking 1756...")
        e = Edital.query.filter_by(numero='1756').first()
        if e:
            print(f"Edital 1756 already exists with ID {e.id}")
        else:
            print("Creating Edital 1756...")
            try:
                e = Edital(
                    numero='1756',
                    descricao='CT-FA - CONV 110/2025 - MESTRADO & DOUTORADO - 3793-1 - 15277-6',
                    agencia='Fundação Araucária'
                )
                db.session.add(e)
                db.session.commit()
                print(f"Edital 1756 Created! ID: {e.id}")
                
                 # Dates
                e.data_inicio = date(2025, 1, 1)
                e.data_fim = date(2026, 12, 31)
                db.session.commit()

                # Modalidades
                m1 = Modalidade(edital_id=e.id, nivel='Mestrado', vagas=10, valor_mensal=2100.0)
                m2 = Modalidade(edital_id=e.id, nivel='Doutorado', vagas=10, valor_mensal=3100.0)
                db.session.add_all([m1, m2])
                db.session.commit()
                print("Modalidades mestre/doutor added.")
            except Exception as ex:
                db.session.rollback()
                print(f"ERROR Creating 1756: {ex}")

if __name__ == "__main__":
    force_1756()
