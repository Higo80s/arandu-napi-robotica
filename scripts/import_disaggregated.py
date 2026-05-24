import sys
import os
import pandas as pd
import unicodedata

# Contexto da Aplicação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import ProgramaAcademico, BolsaVolumetriaAnual, AgenciaFomento

BASE_DIR = r"planilnhas_externas"
FILES = {
    'Mestrado': "_PROPPG_15 - Número de bolsas de mestrado nos programas acadêmicos e profissionais 2025.xlsx",
    'Doutorado': "_PROPPG_17 - Número de bolsas nos programas de doutorado da UTFPR.xlsx"
}

# Mapping Agencias to IDs (Same as import_consolidated.py)
AGENCY_MAP = {
    'CAPES_PPG': 1,
    'CAPES_IES_PROPPG': 1, # Treat as CAPES
    'CNPQ': 2,
    'CNPq': 2,
    'OUTRAS': 4,
    'FUNDAÇÃO ARAUCÁRIA': 4,
    'RECURSOS, PROPRÍOS, FUNDAÇÃO ARAUCÁRIA': 4
}

def normalize_col(col_name):
    """Normalize column names to handle variations like 'Agência', 'agencia', 'tipo ', 'tipo'"""
    if isinstance(col_name, int): return str(col_name)
    s = str(col_name).lower().strip()
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII')
    return s

def get_program_id(sigla, campus_sigla):
    """Find program ID by Sigla and Campus. Cache this if performance is an issue."""
    # Try exact match first
    prog = ProgramaAcademico.query.join(ProgramaAcademico.campus).filter(
        ProgramaAcademico.sigla_programa == sigla,
        ProgramaAcademico.campus.has(sigla_campus=campus_sigla)
    ).first()
    
    if prog:
        return prog.id
    return None

def run():
    print("--- Importação Desagregada (Mestrado/Doutorado) ---")
    
    with app.app_context():
        total_inserted = 0
        total_wiped = 0
        
        for nivel_label, filename in FILES.items():
            file_path = os.path.join(BASE_DIR, filename)
            if not os.path.exists(file_path):
                print(f"[ERRO] Arquivo não encontrado: {file_path}")
                continue
                
            print(f"Processando: {nivel_label} ({filename})...")
            try:
                df = pd.read_excel(file_path)
            except Exception as e:
                print(f"[ERRO] Falha ao ler Excel: {e}")
                continue

            # Normalize columns
            df.columns = [normalize_col(c) for c in df.columns]
            
            # Identify Year Columns (2014-2025)
            year_cols = [c for c in df.columns if c.isdigit() and 2014 <= int(c) <= 2025]
            print(f"Colunas de Ano identificadas: {year_cols}")
            
            # Identify Metadata Columns
            col_sigla = next((c for c in df.columns if 'sigla' in c), None)
            col_campus = next((c for c in df.columns if 'campus' in c), None)
            col_agencia = next((c for c in df.columns if 'agencia' in c), None)
            
            if not all([col_sigla, col_campus, col_agencia]):
                print(f"[ERRO] Colunas obrigatórias não encontradas. Sigla: {col_sigla}, Campus: {col_campus}, Agencia: {col_agencia}")
                continue

            # Process Rows
            for idx, row in df.iterrows():
                sigla = str(row[col_sigla]).strip().upper()
                campus = str(row[col_campus]).strip().upper()
                
                # Normalize Campus Sigla (Handle variations if any, matching import_consolidated logic ideally)
                # Assuming standard siglas roughly match DB or using helpers if needed. 
                # For now using strict match from DB cache would be better, but let's try direct.
                # DB Campus Siglas: CP, CT, DV, FB, GP, LD, MD, PB, PG, SH, TD
                
                prog_id = get_program_id(sigla, campus)
                if not prog_id:
                     # Try mapping keys
                     campus_map = {'CURITIBA': 'CT', 'PONTA GROSSA': 'PG', 'PATO BRANCO': 'PB', 'CORNELIO PROCOPIO': 'CP', 'MEDIANEIRA': 'MD', 'LONDRINA': 'LD', 'APUCARANA': 'AP', 'CAMPO MOURAO': 'CM', 'DOIS VIZINHOS': 'DV', 'FRANCISCO BELTRAO': 'FB', 'GUARAPUAVA': 'GP', 'SANTA HELENA': 'SH', 'TOLEDO': 'TD'}
                     campus = campus_map.get(campus, campus)
                     prog_id = get_program_id(sigla, campus)
                
                if not prog_id:
                    # Special case for CP/UEL if needed
                    if 'UEL' in str(row).upper():
                        campus = 'CP' # Assumption for PPGAEE
                        prog_id = get_program_id(sigla, campus)

                if not prog_id:
                    # print(f"Programa não encontrado: {sigla} - {campus}")
                    continue

                # Parse Agencia
                agencia_raw = str(row[col_agencia]).upper().strip()
                # Simple loose matching
                agencia_id = 4 # Default Outras
                for key, val in AGENCY_MAP.items():
                    if key in agencia_raw:
                        agencia_id = val
                        break
                
                # WIPE existing data for this Program + Nivel + Agencia only?
                # Or WIPE ALL for this Program to properly reset?
                # Strategy: WIPE all 'Mestrado/Doutorado' mix entries first?
                # Better: Upsert. But we need to clear previous 'aggregated' data if it exists.
                # If we run this AFTER import_consolidated, validation logic:
                # User decided to REPLACE aggregated data.
                # Query existing entries for this Prog + Year and DELETE if Nivel is 'Mestrado/Doutorado' OR matches current nivel
                
                for year_str in year_cols:
                    ano = int(year_str)
                    qtd = row[year_str]
                    try:
                        qtd = int(qtd)
                    except:
                        qtd = 0
                        
                    # DATA CLEANUP LOGIC
                    # If we are inserting 'Mestrado', ensure no 'Mestrado/Doutorado' exists for this year.
                    # Also ensure no payload for 'Mestrado' exists (overwrite).
                    
                    # 1. Delete 'Mestrado/Doutorado' (Aggregated)
                    db.session.query(BolsaVolumetriaAnual).filter(
                        BolsaVolumetriaAnual.programa_id == prog_id,
                        BolsaVolumetriaAnual.ano_referencia == ano,
                        BolsaVolumetriaAnual.nivel == 'Mestrado/Doutorado'
                    ).delete()
                    
                    # 2. Upsert specific level
                    vol = BolsaVolumetriaAnual.query.filter_by(
                        programa_id=prog_id,
                        ano_referencia=ano,
                        agencia_id=agencia_id,
                        nivel=nivel_label
                    ).first()
                    
                    if not vol:
                        vol = BolsaVolumetriaAnual(
                            programa_id=prog_id,
                            ano_referencia=ano,
                            agencia_id=agencia_id,
                            nivel=nivel_label
                        )
                        db.session.add(vol)
                    
                    vol.qtd_sistema = qtd
                    # Preserve manual edits if any? Assuming excel overrides system count.
                    
                    total_inserted += 1
                
        try:
            db.session.commit()
            print(f"Sucesso! Registros processados: {total_inserted}")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao commitar: {e}")

if __name__ == "__main__":
    run()
