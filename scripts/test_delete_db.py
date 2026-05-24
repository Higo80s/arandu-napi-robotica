import sys
import os

# Set up paths so we can import from the Flask app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Modalidade, Bolsista, Residente

with app.app_context():
    mod_id = 57 # As reported by the user
    print(f"Buscando Modalidade {mod_id}...")
    
    mod = Modalidade.query.get(mod_id)
    if not mod:
        print("Modalidade não encontrada!")
        sys.exit(1)
        
    print(f"Modalidade: {mod.nivel} - Vagas: {mod.vagas}")
    print(f"Bolsistas vinculados: {len(mod.bolsistas)}")
    
    # Check if there are Residentes linked (just in case they use this model)
    res = Residente.query.filter_by(modalidade_id=mod.id).count()
    print(f"Residentes vinculados: {res}")
    
    try:
        print("Tentando excluir (dry run)..")
        db.session.delete(mod)
        db.session.commit()
        print("EXCLUÍDO COM SUCESSO!")
    except Exception as e:
        db.session.rollback()
        print("\n=== ERRO AO EXCLUIR ===")
        print(e)
        
