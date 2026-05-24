import os
import sys
import pandas as pd
from sqlalchemy import text
import json

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import Bolsista, ProgramaAcademico
from encryption import cipher_suite

def analyze_deeply():
    base_dir = os.path.join(app.root_path, 'planilnhas_externas', 'capes')
    file_ppg = os.path.join(base_dir, 'capes_cotas_ppg.xlsx')

    # 1. Duplicates Check (DB)
    print("Verificando duplicados no banco (Editais 13 e 14)...")
    with app.app_context():
        bolsistas = Bolsista.query.filter(
            Bolsista.edital_id.in_([13, 14]),
            db.or_(Bolsista.ativo == True, Bolsista.motivo_desligamento == 'Finalizando')
        ).all()
        
        cpf_counts = {}
        for b in bolsistas:
            if not b.cpf: continue
            try:
                raw_cpf = cipher_suite.decrypt(b.cpf.encode('utf-8')).decode('utf-8') if b.cpf.startswith('gAAAAA') else b.cpf
                clean_cpf = raw_cpf.replace('.', '').replace('-', '').strip()
                if clean_cpf not in cpf_counts: cpf_counts[clean_cpf] = []
                cpf_counts[clean_cpf].append(f"{b.id}: {b.nome} ({b.edital_id})")
            except: continue
        
        duplicates = {cpf: info for cpf, info in cpf_counts.items() if len(info) > 1}
        print(f"Bolsistas com CPF duplicado no banco: {len(duplicates)}")
        if duplicates:
            with open('dubplicados_cpf.json', 'w', encoding='utf-8') as f:
                json.dump(duplicates, f, indent=4, ensure_ascii=False)

    # 2. Program Quotas Comparison
    print("Comparando cotas por programa (Excel vs Banco)...")
    df_ppg = pd.read_excel(file_ppg, skiprows=4, header=None)
    # Col 4: PPG/Área (Ex: "40006018044P2 - ADMINISTRAÇÃO"), Col 2: Modalidade, Col 5: Concedida
    excel_quotas = {} # code -> {mestrado: X, doutorado: Y}
    
    for _, row in df_ppg.iterrows():
        area = str(row[4]).strip()
        if ' - ' not in area: continue
        code = area.split(' - ')[0].strip()
        mod = str(row[2]).strip()
        concedida = row[5]
        if pd.isna(concedida) or not isinstance(concedida, (int, float)): continue
        
        if code not in excel_quotas: excel_quotas[code] = {"mestrado": 0, "doutorado": 0, "nome": area.split(' - ')[1].strip()}
        key = "mestrado" if "Mestrado" in mod else "doutorado"
        excel_quotas[code][key] += int(concedida)

    with app.app_context():
        sql = """
        SELECT p.codigo_programa, m.nivel, SUM(c.qtd_concedida) as total
        FROM distribuicao_cotas c
        JOIN programa_academico p ON c.programa_id = p.id
        JOIN modalidades m ON c.modalidade_id = m.id
        WHERE c.edital_id = 14
        GROUP BY p.codigo_programa, m.nivel
        """
        res = db.session.execute(text(sql))
        db_quotas = {}
        for r in res:
            code = r.codigo_programa
            if code not in db_quotas: db_quotas[code] = {"mestrado": 0, "doutorado": 0}
            key = "mestrado" if "Mestrado" in r.nivel else "doutorado"
            db_quotas[code][key] = int(r.total)

        # Cross comparison
        discrepancies = []
        all_codes = set(excel_quotas.keys()) | set(db_quotas.keys())
        for code in all_codes:
            ex = excel_quotas.get(code, {"mestrado": 0, "doutorado": 0, "nome": "N/A"})
            db_q = db_quotas.get(code, {"mestrado": 0, "doutorado": 0})
            
            if ex["mestrado"] != db_q["mestrado"] or ex["doutorado"] != db_q["doutorado"]:
                discrepancies.append({
                    "codigo": code,
                    "nome": ex["nome"],
                    "excel": ex,
                    "banco": db_q
                })
        
        print(f"Programas com cotas divergentes: {len(discrepancies)}")
        with open('cotas_divergentes.json', 'w', encoding='utf-8') as f:
            json.dump(discrepancies, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    analyze_deeply()
