import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Bolsista, Edital

def check_b():
    with app.app_context():
        print("--- CHECKING BOLSISTAS IN POSTGRES ---")
        
        # Edital 1357 (ID 3)
        e3 = db.session.get(Edital, 3)
        if e3:
            bs = Bolsista.query.filter_by(edital_id=3).all()
            print(f"Edital 1357 (ID 3): Found {len(bs)} bolsistas")
            for b in bs:
                print(f"  - {b.nome} (Ativo: {b.ativo})")
                
        # Edital 1756 (ID 32 - assumed from previous steps, checking dynamically)
        e1756 = Edital.query.filter(Edital.numero.like('%1756%')).first()
        if e1756:
            bs = Bolsista.query.filter_by(edital_id=e1756.id).all()
            print(f"Edital 1756 (ID {e1756.id}): Found {len(bs)} bolsistas")
            for b in bs:
                print(f"  - {b.nome} (Ativo: {b.ativo})")
        else:
             print("Edital 1756 not found in DB structure check")

if __name__ == "__main__":
    check_b()
