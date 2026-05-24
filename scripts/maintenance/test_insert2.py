"""Simple test insert with full error capture."""
import sys
sys.path.insert(0, '.')

from app import app
from models import db, Bolsista, Modalidade
from utils import parse_flexible_date
from datetime import date

with app.app_context():
    print("=== Testing Single Insert ===")
    
    # Get first available CAPES Doutorado modalidade
    mod = None
    for m in Modalidade.query.all():
        if m.nivel == 'Doutorado' and m.edital.agencia and 'CAPES' in m.edital.agencia.upper():
            mod = m
            break
    
    if not mod:
        print("ERROR: No CAPES Doutorado modalidade found!")
        sys.exit(1)
    
    print(f"Using: Edital {mod.edital_id} ({mod.edital.agencia}), Modalidade {mod.id} ({mod.nivel})")
    
    try:
        dt_ini = parse_flexible_date("01/08/2024")
        dt_fim = parse_flexible_date("31/07/2028")
        meses = 48
        
        print(f"Dates: {dt_ini} to {dt_fim}, meses={meses}")
        
        bolsista = Bolsista(
            nome="TESTE DEYSE",
            cpf="999.888.777-66",
            edital_id=mod.edital_id,
            modalidade_id=mod.id,
            programa_id=None,
            data_inicio_bolsa=dt_ini,
            data_fim_bolsa=dt_fim,
            meses_duracao=meses,
            ativo=True
        )
        
        db.session.add(bolsista)
        db.session.commit()
        print(f"SUCCESS! ID={bolsista.id}")
        
        # Cleanup
        db.session.delete(bolsista)
        db.session.commit()
        print("Cleanup done.")
        
    except Exception as e:
        db.session.rollback()
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
