import os
import sys
import pandas as pd
from datetime import datetime
import shutil

# Add the parent directory to the path so we can import models and app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import EncryptedString, Bolsista, Residente, Edital, Modalidade

PLANILHAS_DIR = r"c:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo\planilnhas_externas\fundacao_araucaria\fundacao_araucaria_extrato_individual_projetos"
TODOS_CSV = r"c:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo\planilnhas_externas\fundacao_araucaria\Alunos_bolsistas_todos.csv"
DB_PATH = r"c:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo\gestao_editais_final.db"
BACKUP_PATH = DB_PATH + ".bak_" + datetime.now().strftime("%Y%m%d_%H%M%S")

# ID of the newly created Generic Edital
GENERIC_EDITAL_ID = 14 

# Nivel mapping based on FA spreadsheet
NIVEL_MAP = {
    'Mestrado': 'Mestrado',
    'Doutorado': 'Doutorado',
    'Graduação': 'Iniciação Científica',
    'Pós-Doutorado': 'Pós-Doutorado',
    'Sênior': 'Pesquisador Sênior'
}

def backup_db():
    print(f"Creating DB backup at {BACKUP_PATH}...")
    shutil.copy2(DB_PATH, BACKUP_PATH)

def run_update(dry_run=True):
    print(f"Starting FA Project Update... [DRY_RUN={dry_run}]")
    
    if not dry_run:
        backup_db()
        
    with app.app_context():
        # 1. Read all the FA Spreadsheets to get the active/valid list of Bolsistas
        valid_bolsistas = [] # List of tuples: (Nome, Projeto, Nivel, Parcelas)
        projeto_info = {} # mapping from filename to project name
        
        for file in os.listdir(PLANILHAS_DIR):
            if file.endswith(('.xlsx', '.xlsm')):
                filepath = os.path.join(PLANILHAS_DIR, file)
                try:
                    df = pd.read_excel(filepath)
                    for _, row in df.iterrows():
                        # Based on our debug JSON, column names typically exist:
                        # nome_bolsista, Projeto, Nível, Total de Parcelas
                        if pd.notna(row.get('nome_bolsista')) and str(row.get('nome_bolsista')).strip():
                            nome = str(row['nome_bolsista']).strip()
                            projeto = str(row.get('Projeto', ''))
                            nivel = str(row.get('Nível', ''))
                            parcelas = row.get('Total de Parcelas')
                            parcelas = int(parcelas) if pd.notna(parcelas) else 0
                            
                            valid_bolsistas.append({
                                'nome': nome,
                                'projeto': projeto,
                                'nivel': nivel,
                                'parcelas': parcelas,
                                'file': file
                            })
                            if projeto and file not in projeto_info:
                                projeto_info[file] = projeto
                except Exception as e:
                    print(f"Error reading {file}: {e}")

        print(f"\nFound {len(valid_bolsistas)} valid bolsistas across {len(projeto_info)} project valid spreadsheets.")
        
        # 2. Iterate through ALL FA Bolsistas in DB and compare
        # Assuming we can identify FA bolsistas implicitly by their current Edital, or via the CSV
        
        # Read the general CSV for FA
        all_fa_names_in_csv = set()
        if os.path.exists(TODOS_CSV):
            # TODO: Add logic to read ALL FA names from the CSV once we verify its structure
            pass
        
        # Let's perform DB matching
        matched_db_ids = set()
        
        print("\n--- Processing Valid Bolsistas from Spreadsheets ---")
        for vb in valid_bolsistas:
            nome_upper = vb['nome'].upper()
            
            # Find in Bolsista table (case-insensitive)
            b = Bolsista.query.filter(db.func.upper(Bolsista.nome).like(f"%{nome_upper}%")).first()
            if b:
                matched_db_ids.add(b.id)
                # Check mapping
                if b.meses_duracao != vb['parcelas']:
                    print(f"[{vb['nome']}] Duration mismatch: DB={b.meses_duracao}, Sheet={vb['parcelas']}. Fixing to {vb['parcelas']}.")
                    if not dry_run:
                        b.meses_duracao = vb['parcelas']
                        
                # Ensure it's active
                if not b.ativo:
                    print(f"[{vb['nome']}] Marking as ACTIVE (was inactive).")
                    if not dry_run:
                        b.ativo = True
                
                # Check Nivel (via Modalidade)
                expected_nivel = NIVEL_MAP.get(vb['nivel'], vb['nivel'])
                if b.modalidade and b.modalidade.nivel != expected_nivel:
                   print(f"[{vb['nome']}] Nivel mismatch: DB={b.modalidade.nivel}, Sheet={expected_nivel}. Needs manual Modalidade map if changing.")
                   
            else:
                 # Check Residente table
                 r = Residente.query.filter(db.func.upper(Residente.nome).like(f"%{nome_upper}%")).first()
                 if r:
                     if r.meses_duracao != vb['parcelas']:
                        print(f"[{vb['nome']}] [RESIDENTE] Duration mismatch: DB={r.meses_duracao}, Sheet={vb['parcelas']}. Fixing to {vb['parcelas']}.")
                        if not dry_run:
                            r.meses_duracao = vb['parcelas']
                 else:
                     print(f"[{vb['nome']}] WARNING: Not found in database at all!")

        print("\n--- Identifying Unregistered FA Bolsistas (Análise Posterior & Desligamento) ---")
        # Logic: We need to pull all bolsistas currently linked to Araucária in DB that weren't matched.
        # Find Editais for Araucária
        fa_editais = Edital.query.filter(Edital.agencia.ilike('%Arauc%')).all()
        fa_ed_ids = [e.id for e in fa_editais if e.id != GENERIC_EDITAL_ID] # Exclude the generic one
        
        unregistered = Bolsista.query.filter(Bolsista.edital_id.in_(fa_ed_ids), Bolsista.ativo == True).all()
        
        for u in unregistered:
            if u.id not in matched_db_ids:
                print(f"Unlisted Bolsista: {u.nome} (Ativo=True, Current Edital={u.edital.numero}) -> Moving to Generic Edital (Análise Posterior).")
                if not dry_run:
                    # Move to Generic Edital
                    u.edital_id = GENERIC_EDITAL_ID
                    
                    # NOTE: Mudar Modalidade também seria ideal aqui, ou criar uma Modalidade genérica sob o Edital 14.
                    # Por hora, mantemos a Modalidade, mas ela estaria sob o outro Edital, o que tecnicamente fere a FK se for restrito.
                    # Let's ensure a generic Modalidade exists.
                    mod = Modalidade.query.filter_by(edital_id=GENERIC_EDITAL_ID, nivel='Análise').first()
                    if not mod:
                        mod = Modalidade(edital_id=GENERIC_EDITAL_ID, nivel='Análise', vagas=999, valor_mensal=0.0)
                        db.session.add(mod)
                        db.session.commit()
                        
                    u.modalidade_id = mod.id
                    u.ativo = False # Desativar por segurança até análise
                    u.comentarios = f"Movido para análise posterior em {datetime.now().strftime('%Y-%m-%d')}. " + (u.comentarios or "")
                    
        
        if not dry_run:
            db.session.commit()
            print("\nDatabase changes committed.")
        else:
            print("\nDRY RUN completed. No changes made.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true', help="Make actual DB changes")
    args = parser.parse_args()
    
    run_update(dry_run=not args.execute)
