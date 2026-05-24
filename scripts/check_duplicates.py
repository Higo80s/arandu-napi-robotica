import os
import sys
from sqlalchemy import text
import json

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import Bolsista
from encryption import cipher_suite

def check_duplicates():
    with app.app_context():
        bolsistas = Bolsista.query.filter(
            Bolsista.edital_id.in_([13, 14]),
            db.or_(Bolsista.ativo == True, Bolsista.motivo_desligamento == 'Finalizando')
        ).all()
        
        print(f"Bolsistas Ativos/Finalizando no Banco: {len(bolsistas)}")
        
        data = []
        for b in bolsistas:
            cpf = "N/A"
            if b.cpf:
                try:
                    cpf = cipher_suite.decrypt(b.cpf.encode('utf-8')).decode('utf-8') if b.cpf.startswith('gAAAAA') else b.cpf
                    cpf = cpf.replace('.', '').replace('-', '').strip()
                except: pass
            
            data.append({
                "id": b.id,
                "nome": b.nome,
                "cpf": cpf,
                "edital": b.edital_id,
                "nivel": b.modalidade.nivel if b.modalidade else "N/A",
                "status": "Ativo" if b.ativo else b.motivo_desligamento
            })
            
        # Find duplicates by CPF
        from collections import Counter
        cpfs = [d["cpf"] for d in data if d["cpf"] != "N/A"]
        counts = Counter(cpfs)
        
        dups = {cpf: count for cpf, count in counts.items() if count > 1}
        print(f"Total de CPFs duplicados: {len(dups)}")
        
        dup_list = []
        for cpf, count in dups.items():
            matching = [d for d in data if d["cpf"] == cpf]
            dup_list.append({
                "cpf": cpf,
                "count": count,
                "records": matching
            })
            
        with open('audit_duplicates.json', 'w', encoding='utf-8') as f:
            json.dump(dup_list, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    check_duplicates()
