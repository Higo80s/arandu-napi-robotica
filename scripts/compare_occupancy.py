import os
import sys
import pandas as pd
from sqlalchemy import text

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import app, db

def compare_full():
    base_dir = os.path.join(app.root_path, 'planilnhas_externas', 'capes')
    file_ppg = os.path.join(base_dir, 'capes_cotas_ppg.xlsx')
    
    # Precise ppg read
    df_ppg = pd.read_excel(file_ppg, skiprows=4)
    # The columns are not always named 'Código do Programa' if there's a multi-index feel.
    # Let's use position. 
    # Col 0: Código, Col 1: Programa, Col 2: Nível, Col 3: Concedida, Col 4: Utilizada, Col 5: Disponível
    
    excel_data = {}
    for _, row in df_ppg.iterrows():
        code = str(row.iloc[0]).strip()
        nivel = str(row.iloc[2]).strip()
        used = row.iloc[4]
        if code and nivel and not pd.isna(used):
            excel_data[(code, nivel)] = int(used)

    with app.app_context():
        sql = """
            SELECT p.codigo_programa, m.nivel, COUNT(*) as count
            FROM bolsistas b
            JOIN modalidades m ON b.modalidade_id = m.id
            JOIN programa_academico p ON b.programa_id = p.id
            WHERE (b.ativo = True OR b.motivo_desligamento = 'Finalizando') AND b.edital_id = 14
            GROUP BY p.codigo_programa, m.nivel
        """
        db_res = db.session.execute(text(sql)).all()
        
        with open('mismatch_report.txt', 'w', encoding='utf-8') as f:
            for r in db_res:
                code = r.codigo_programa
                nivel = r.nivel
                db_count = r.count
                ex_count = excel_data.get((code, nivel), 0)
                if db_count != ex_count:
                    f.write(f"PROG: {code} | NIVEL: {nivel} | DB: {db_count} | EXCEL: {ex_count} | DIFF: {db_count - ex_count}\n")
        
        print("Mismatches dumped to mismatch_report.txt")

if __name__ == "__main__":
    compare_full()
