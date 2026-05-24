import os
import sys
import pandas as pd
from sqlalchemy import text
import json

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import Bolsista
from encryption import cipher_suite

def find_7_extras():
    base_dir = os.path.join(app.root_path, 'planilnhas_externas', 'capes')
    file_bolsistas = os.path.join(base_dir, 'capes_ppg_todos_bolsistas.xlsx')

    print("Lendo planilha oficial de bolsistas...")
    df = pd.read_excel(file_bolsistas)
    
    excel_cpfs = set()
    for val in df['Beneficiário'].dropna():
        s_val = str(val).strip()
        cpf_part = s_val.split(' - ')[0] if ' - ' in s_val else s_val
        clean_cpf = "".join(filter(str.isdigit, cpf_part))
        if clean_cpf:
            excel_cpfs.add(clean_cpf)

    print(f"Total de CPFs na planilha: {len(excel_cpfs)}")

    with app.app_context():
        db_bolsistas = Bolsista.query.filter(
            Bolsista.edital_id.in_([13, 14]),
            db.or_(Bolsista.ativo == True, Bolsista.motivo_desligamento == 'Finalizando')
        ).all()
        
        print(f"Bolsistas no Banco: {len(db_bolsistas)}")
        
        found_in_excel = 0
        not_found = []
        
        for b in db_bolsistas:
            clean_db_cpf = None
            if b.cpf:
                try:
                    raw_cpf = cipher_suite.decrypt(b.cpf.encode('utf-8')).decode('utf-8') if b.cpf.startswith('gAAAAA') else b.cpf
                    clean_db_cpf = "".join(filter(str.isdigit, raw_cpf))
                except: pass
            
            if clean_db_cpf in excel_cpfs:
                found_in_excel += 1
            else:
                not_found.append({
                    "id": b.id,
                    "nome": b.nome,
                    "cpf": clean_db_cpf,
                    "edital": b.edital_id,
                    "nivel": b.modalidade.nivel if b.modalidade else "N/A"
                })

        print(f"Encontrados na planilha: {found_in_excel}")
        print(f"NÃO encontrados: {len(not_found)}")
        
        for item in not_found:
            print(f"-> {item['nome']} (ID {item['id']}, CPF {item['cpf']}, Edital {item['edital']}, Nível {item['nivel']})")

if __name__ == "__main__":
    find_7_extras()
