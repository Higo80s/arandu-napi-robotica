import os
import sys
import pandas as pd
from sqlalchemy import text
import json

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import app, db
from models import Bolsista, Modalidade, ProgramaAcademico
from encryption import cipher_suite

def reconcile():
    base_dir = os.path.join(app.root_path, 'planilnhas_externas', 'capes')
    file_ppg = os.path.join(base_dir, 'capes_cotas_ppg.xlsx')
    file_ies = os.path.join(base_dir, 'capes_ies.xlsx')

    # 1. Expected PPG (Edital 14)
    df_ppg = pd.read_excel(file_ppg, skiprows=4)
    expected_ppg = {} # (code, level) -> count
    for _, row in df_ppg.iterrows():
        try:
            code = str(row.iloc[0]).strip()
            level = str(row.iloc[2]).strip()
            used = row.iloc[4]
            if code and level and not pd.isna(used):
                expected_ppg[(code, level)] = int(used)
        except: continue

    # 2. Expected IES (Edital 13)
    # Based on debug, IES is simpler: it seems to be المؤسسة level but let's assume it has levels too.
    # In Edital 13, programs are often 'UTFPR' general or specific.
    # Actually Edital 13 matches by Level only for the whole institution?
    # Let's check the dashboard logic for IES:
    # sql_ies = "SELECT nivel, vagas FROM modalidades WHERE edital_id = 13"
    # It doesn't group by program because IES are institution-wide.
    # capes_ies.xlsx said: Doutorado used 6, Mestrado used 10.
    expected_ies = {"Mestrado": 10, "Doutorado": 6}

    with app.app_context():
        # PPG Audit
        sql_ppg = """
            SELECT p.codigo_programa, m.nivel, b.id, b.nome, b.data_fim_bolsa, b.motivo_desligamento
            FROM bolsistas b
            JOIN modalidades m ON b.modalidade_id = m.id
            JOIN programa_academico p ON b.programa_id = p.id
            WHERE (b.ativo = True OR b.motivo_desligamento = 'Finalizando') AND b.edital_id = 14
            ORDER BY p.codigo_programa, m.nivel, b.data_fim_bolsa
        """
        db_ppg = db.session.execute(text(sql_ppg)).all()
        
        # Group by program/level
        db_groups = {}
        for r in db_ppg:
            key = (r.codigo_programa, r.nivel)
            if key not in db_groups: db_groups[key] = []
            db_groups[key].append(r)
            
        extras = []
        for key, members in db_groups.items():
            expected = expected_ppg.get(key, 0)
            if len(members) > expected:
                diff = len(members) - expected
                # Suggest inactivating the ones with earliest data_fim_bolsa or those already 'Finalizando'
                to_inactivate = members[:diff] # Taking the first ones (usually earliest date)
                for b in to_inactivate:
                    extras.append({
                        "id": b.id, "nome": b.nome, "prog": key[0], "nivel": key[1], 
                        "fim": str(b.data_fim_bolsa), "status": b.motivo_desligamento, "edital": 14
                    })

        # IES Audit (Edital 13)
        sql_ies = """
            SELECT m.nivel, b.id, b.nome, b.data_fim_bolsa, b.motivo_desligamento
            FROM bolsistas b
            JOIN modalidades m ON b.modalidade_id = m.id
            WHERE (b.ativo = True OR b.motivo_desligamento = 'Finalizando') AND b.edital_id = 13
            ORDER BY m.nivel, b.data_fim_bolsa
        """
        db_ies = db.session.execute(text(sql_ies)).all()
        ies_groups = {"Mestrado": [], "Doutorado": []}
        for r in db_ies:
            key = "Mestrado" if "mestrado" in r.nivel.lower() else "Doutorado"
            ies_groups[key].append(r)
            
        for key, members in ies_groups.items():
            expected = expected_ies.get(key, 0)
            if len(members) > expected:
                diff = len(members) - expected
                to_inactivate = members[:diff]
                for b in to_inactivate:
                    extras.append({
                        "id": b.id, "nome": b.nome, "prog": "IES", "nivel": key, 
                        "fim": str(b.data_fim_bolsa), "status": b.motivo_desligamento, "edital": 13
                    })

        with open('final_extras_to_inactivate.json', 'w', encoding='utf-8') as f:
            json.dump(extras, f, indent=4, ensure_ascii=False)
            
        print(f"Total extras identified: {len(extras)}")
        for e in extras:
            print(f"- {e['nome']} (ID {e['id']}, {e['nivel']}, {e['prog']}, Fim: {e['fim']})")

if __name__ == "__main__":
    reconcile()
