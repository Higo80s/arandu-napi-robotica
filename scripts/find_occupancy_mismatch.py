import os
import sys
import pandas as pd
from sqlalchemy import text
import json

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import app, db
from models import ProgramaAcademico, Modalidade

def find_occupancy_mismatch():
    base_dir = os.path.join(app.root_path, 'planilnhas_externas', 'capes')
    file_ppg = os.path.join(base_dir, 'capes_cotas_ppg.xlsx')
    file_ies = os.path.join(base_dir, 'capes_ies.xlsx')

    # Read PPG Excel (starts at row 5)
    df_ppg = pd.read_excel(file_ppg, skiprows=4)
    df_ppg.columns = [str(c).strip() for c in df_ppg.columns]
    # Keys: 'Código do Programa', 'Nível', 'Utilizada'
    
    excel_ppg = {} # (code, level) -> used
    for _, row in df_ppg.iterrows():
        code = str(row.get('Código do Programa', '')).strip()
        nivel = str(row.get('Nível', '')).strip()
        used = row.get('Utilizada', 0)
        if code and nivel:
            excel_ppg[(code, nivel)] = int(used) if not pd.isna(used) else 0

    # Read IES Excel
    df_ies = pd.read_excel(file_ies) # Assuming standard structure for IES
    # IES is a bit different, often one row per program
    # Let's see columns
    print("Colunas IES:", df_ies.columns.tolist())
    
    with app.app_context():
        # PPG (Edital 14)
        sql = """
            SELECT p.codigo_programa, m.nivel, COUNT(*) as count
            FROM bolsistas b
            JOIN modalidades m ON b.modalidade_id = m.id
            JOIN programa_academico p ON b.programa_id = p.id
            WHERE (b.ativo = True OR b.motivo_desligamento = 'Finalizando') AND b.edital_id = 14
            GROUP BY p.codigo_programa, m.nivel
        """
        db_ppg_res = db.session.execute(text(sql)).all()
        
        print("\n--- Discrepâncias de Ocupação PPG (DB vs Excel) ---")
        for r in db_ppg_res:
            code = r.codigo_programa
            nivel = r.nivel
            db_count = r.count
            ex_count = excel_ppg.get((code, nivel), 0)
            if db_count > ex_count:
                print(f"Programa {code} ({nivel}): DB={db_count}, Excel={ex_count} -> +{db_count-ex_count}")

if __name__ == "__main__":
    find_occupancy_mismatch()
