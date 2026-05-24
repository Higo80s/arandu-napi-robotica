import os
import sys
from datetime import date
from sqlalchemy import text

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import Bolsista

def check_dates():
    with app.app_context():
        hoje = date(2026, 3, 1)
        bolsistas = Bolsista.query.filter(
            Bolsista.edital_id.in_([13, 14]),
            db.or_(Bolsista.ativo == True, Bolsista.motivo_desligamento == 'Finalizando')
        ).all()
        
        vencidos_ativos = []
        for b in bolsistas:
            if b.data_fim_bolsa < hoje and b.ativo == True:
                vencidos_ativos.append(f"{b.id}: {b.nome} ({b.data_fim_bolsa})")
        
        print(f"Bolsistas Ativos com data fim < {hoje}: {len(vencidos_ativos)}")
        for v in vencidos_ativos:
            print(f" - {v}")

if __name__ == "__main__":
    check_dates()
