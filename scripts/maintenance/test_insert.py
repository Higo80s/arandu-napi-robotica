"""Test insert to debug SQL errors."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Bolsista, ProgramaAcademico
from utils import parse_flexible_date

with app.app_context():
    print("Testing single insert...")
    
    # Find a valid edital/modalidade combo
    from models import Edital, Modalidade
    mod = Modalidade.query.filter(Modalidade.nivel == 'Doutorado').first()
    if not mod:
        print("No Doutorado modalidade found!")
        sys.exit(1)
    print(f"Using edital_id={mod.edital_id}, modalidade_id={mod.id}")
    
    # Try insert
    try:
        bolsista = Bolsista(
            nome="TESTE DEYSE",
            cpf="999.888.777-66",
            edital_id=mod.edital_id,
            modalidade_id=mod.id,
            ativo=True
        )
        db.session.add(bolsista)
        db.session.commit()
        print(f"SUCCESS! Inserted bolsista with id={bolsista.id}")
        
        # Cleanup
        db.session.delete(bolsista)
        db.session.commit()
        print("CLEANUP: Test record deleted.")
    except Exception as e:
        db.session.rollback()
        print(f"FAILED! Error: {e}")
        import traceback
        traceback.print_exc()
