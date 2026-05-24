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

def find_discrepancies():
    base_dir = os.path.join(app.root_path, 'planilnhas_externas', 'capes')
    file_bolsistas = os.path.join(base_dir, 'capes_ppg_todos_bolsistas.xlsx')

    # 1. Load Excel Bolsistas
    print("Lendo planilha oficial de bolsistas...")
    df = pd.read_excel(file_bolsistas)
    # The column is "Beneficiário" and format is "CPF - Nome"
    # Example: "058.854.179-62 - ALANA MILCHESKI"
    excel_cpfs = set()
    for val in df['Beneficiário'].dropna():
        if ' - ' in str(val):
            cpf_part = str(val).split(' - ')[0].strip()
            clean_cpf = cpf_part.replace('.', '').replace('-', '')
            excel_cpfs.add(clean_cpf)

    print(f"Total de CPFs únicos na planilha: {len(excel_cpfs)}")

    # 2. Load DB Bolsistas
    print("Consultando banco de dados (Editais 13 e 14)...")
    results = {
        "no_banco_nao_na_planilha": [],
        "na_planilha_nao_no_banco": []
    }

    with app.app_context():
        # Only active or finalizing
        bolsistas = Bolsista.query.filter(
            Bolsista.edital_id.in_([13, 14]),
            db.or_(Bolsista.ativo == True, Bolsista.motivo_desligamento == 'Finalizando')
        ).all()

        db_cpfs = {} # clean_cpf -> bolsista_obj
        
        for b in bolsistas:
            clean_db_cpf = None
            if b.cpf:
                try:
                    raw_cpf = cipher_suite.decrypt(b.cpf.encode('utf-8')).decode('utf-8') if b.cpf.startswith('gAAAAA') else b.cpf
                    clean_db_cpf = raw_cpf.replace('.', '').replace('-', '').strip()
                except:
                    continue
            
            if clean_db_cpf:
                db_cpfs[clean_db_cpf] = b
                if clean_db_cpf not in excel_cpfs:
                    results["no_banco_nao_na_planilha"].append({
                        "id": b.id,
                        "nome": b.nome,
                        "cpf": clean_db_cpf,
                        "edital": b.edital_id,
                        "status": "Ativo" if b.ativo else b.motivo_desligamento
                    })

    print(f"Bolsistas no banco que NÃO estão na planilha oficial: {len(results['no_banco_nao_na_planilha'])}")
    
    # Save results
    with open('bolsistas_excedentes.json', 'w', encoding='utf-8') as f:
        json.dump(results["no_banco_nao_na_planilha"], f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    find_discrepancies()
