import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Edital, Modalidade

def check_final():
    with app.app_context():
        print("--- FINAL POSTGRES CHECK ---")
        
        # 1357
        e1357 = Edital.query.filter(Edital.numero.like('%1357%')).first()
        if e1357:
            print(f"Edital 1357: FOUND via LIKE match. ID={e1357.id} Num='{e1357.numero}'")
            # Check Modalidade
            m = Modalidade.query.filter_by(edital_id=e1357.id).all()
            print(f"  Modalidades: {[x.nivel for x in m]}")
        else:
            print("Edital 1357: NOT FOUND")

        # 1756
        e1756 = Edital.query.filter(Edital.numero.like('%1756%')).first()
        if e1756:
            print(f"Edital 1756: FOUND via LIKE match. ID={e1756.id} Num='{e1756.numero}'")
             # Check Modalidade
            m = Modalidade.query.filter_by(edital_id=e1756.id).all()
            print(f"  Modalidades: {[x.nivel for x in m]}")
        else:
            print("Edital 1756: NOT FOUND")

if __name__ == "__main__":
    check_final()
