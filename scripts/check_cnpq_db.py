import sys
import os
from sqlalchemy import text

# Contexto da Aplicação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import BolsaVolumetriaAnual, AgenciaFomento

def run():
    print("--- CHECK CNPQ DATA ---")
    with app.app_context():
        # Check Agencies
        agencies = AgenciaFomento.query.all()
        print("Agencies in DB:")
        for a in agencies:
            print(f"ID: {a.id} Name: {a.nome}")
            
        # Check specific records for CNPq (ID 3)
        cnpq_count = BolsaVolumetriaAnual.query.filter_by(agencia_id=3).count()
        print(f"\nTotal CNPq Records in Volumetria: {cnpq_count}")
        
        if cnpq_count > 0:
            samples = BolsaVolumetriaAnual.query.filter_by(agencia_id=3).limit(5).all()
            for s in samples:
                print(f"Sample: Year={s.ano_referencia} Qtd={s.qtd_sistema} Nivel='{s.nivel}'")
            
        # Check distinct levels for CNPq
        distinct_levels = db.session.query(BolsaVolumetriaAnual.nivel).filter_by(agencia_id=3).distinct().all()
        print(f"Distinct Levels for CNPq: {[r[0] for r in distinct_levels]}")

if __name__ == '__main__':
    run()
