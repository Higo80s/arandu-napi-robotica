
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from app import app
from models import db, Bolsista, Edital, Acompanhamento
from datetime import date

def diagnose():
    with app.app_context():
        # Find Fundação Araucária editais
        fa_editais = Edital.query.filter(Edital.agencia.ilike('%Araucária%')).all()
        fa_ids = [e.id for e in fa_editais]
        
        print(f"Found {len(fa_editais)} Fundação Araucária editais: {[e.numero for e in fa_editais]}")
        
        # Active FA bolsistas
        active_fa = Bolsista.query.filter(Bolsista.edital_id.in_(fa_ids), Bolsista.ativo == True).all()
        print(f"Total active FA bolsistas: {len(active_fa)}")
        
        # Missing CPF
        missing_cpf = [b for b in active_fa if not b.cpf]
        print(f"Scholars without CPF: {len(missing_cpf)}")
        for b in missing_cpf[:5]:
            print(f" - ID: {b.id}, Nome: {b.nome}, SEI: {b.processo_sei}")
            
        # Check last parcels (Feb 2026)
        feb_ref = "2026-02"
        acomp_feb = Acompanhamento.query.filter(Acompanhamento.referencia_mes == feb_ref).all()
        print(f"Acompanhamentos for {feb_ref}: {len(acomp_feb)}")
        
        if active_fa:
            sample = active_fa[0]
            last_acomp = Acompanhamento.query.filter_by(bolsista_id=sample.id).order_by(Acompanhamento.referencia_mes.desc()).first()
            if last_acomp:
                print(f"Sample Scholar {sample.nome} (ID {sample.id}): Last parcel {last_acomp.parcela} in {last_acomp.referencia_mes}")
            else:
                print(f"Sample Scholar {sample.nome} (ID {sample.id}): No acompanhamento found.")

if __name__ == "__main__":
    diagnose()
