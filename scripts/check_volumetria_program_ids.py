import sys
import os
from sqlalchemy import text

# Contexto da Aplicação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import BolsaVolumetriaAnual, ProgramaAcademico, Campus

def run():
    print("--- CHECK VOLUMETRIA PROGRAM IDs ---")
    with app.app_context():
        # Get all CNPq records
        vol_records = BolsaVolumetriaAnual.query.filter_by(agencia_id=3).all()
        print(f"Total CNPq Records: {len(vol_records)}")
        
        missing_progs = 0
        existing_progs = 0
        
        sample_missing = []
        
        for v in vol_records:
            pid = v.programa_id
            prog = ProgramaAcademico.query.get(pid)
            if not prog:
                missing_progs += 1
                if len(sample_missing) < 5: sample_missing.append(pid)
            else:
                existing_progs += 1
                
        print(f"Existing Programs: {existing_progs}")
        print(f"Missing Programs (Invalid FK): {missing_progs}")
        if missing_progs > 0:
            print(f"Sample Missing IDs: {sample_missing}")

        # Check Campus Validity too just in case
        print("\nChecking Campus Links via Program...")
        joined_count = db.session.query(BolsaVolumetriaAnual).join(ProgramaAcademico).join(Campus).filter(BolsaVolumetriaAnual.agencia_id==3).count()
        print(f"Count via JOIN (Prog+Campus): {joined_count}")

if __name__ == '__main__':
    run()
