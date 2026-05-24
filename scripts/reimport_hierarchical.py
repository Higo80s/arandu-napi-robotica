import pandas as pd
import os
import sys

# Contexto da Aplicação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import AgenciaFomento, BolsaVolumetriaAnual, ProgramaAcademico, Campus

# Configuração
BASE_PATH = r"c:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo\planilnhas_externas"
FILES = {
    'Mestrado': {
        'filename': "_PROPPG_15 - Número de bolsas de mestrado nos programas acadêmicos e profissionais 2025.xlsx",
        'header_row': 3,
        'col_name': 1,
        'col_sigla': 2,
        'col_code': 3,
        'col_agency': 4,
        'col_year_start': 5
    },
    'Doutorado': {
        'filename': "_PROPPG_17 - Número de bolsas nos programas de doutorado da UTFPR.xlsx",
        'header_row': 2,
        'col_name': 1,
        'col_sigla': 2,
        'col_code': 4, # Tem coluna 'campus' no meio
        'col_agency': 5,
        'col_year_start': 6
    }
}

def resolve_agencia(agencia_raw, agencias_db):
    """
    Mapeia string da planilha para ID da Agência no Banco.
    """
    if pd.isna(agencia_raw):
        return None
        
    raw = str(agencia_raw).lower().strip()
    
    if 'capes' in raw:
        return agencias_db.get('CAPES')
    elif 'cnpq' in raw:
        return agencias_db.get('CNPq')
    elif 'araucária' in raw or 'araucaria' in raw or 'fundação' in raw or 'propríos' in raw or 'proprios' in raw:
        return agencias_db.get('Fundação Araucária')
    elif 'utfpr' in raw:
        return agencias_db.get('UTFPR')
        
    return None

def process_file(level, config):
    filename = config['filename']
    file_path = os.path.join(BASE_PATH, filename)
    if not os.path.exists(file_path):
        print(f"[{level}] Arquivo não encontrado: {filename}")
        return

    print(f"\n--- Processando {level}: {filename} ---")
    
    # Load Dicts
    agencias_db = {a.sigla: a for a in AgenciaFomento.query.all()}
    progs_by_sigla = {p.sigla_programa: p for p in ProgramaAcademico.query.all()}
    progs_by_code = {p.codigo_programa: p for p in ProgramaAcademico.query.all() if p.codigo_programa}
    
    # Read Excel
    try:
        df = pd.read_excel(file_path, header=config['header_row'])
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return

    # Identify Columns from Config
    c_name = config['col_name']
    c_sigla = config['col_sigla']
    c_code = config['col_code']
    c_agency = config['col_agency']
    c_year_start = config['col_year_start']
    
    curr_prog = None
    stats_buffer = {} 
    
    for idx, row in df.iterrows():
        # 1. Update Program State
        raw_name = row.iloc[c_name] if c_name < len(row) else None
        raw_sigla = row.iloc[c_sigla] if c_sigla < len(row) else None
        raw_code = row.iloc[c_code] if c_code < len(row) else None
        
        if not pd.isna(raw_name) or (c_sigla < len(row) and not pd.isna(raw_sigla)):
            # New Program Block
            p_obj = None
            
            # Try by Code
            if not pd.isna(raw_code):
                clean_code = str(raw_code).strip()
                p_obj = progs_by_code.get(clean_code)
            
            # Try by Sigla
            if not p_obj and not pd.isna(raw_sigla):
                clean_sigla = str(raw_sigla).strip()
                p_obj = progs_by_sigla.get(clean_sigla)
                
            if p_obj:
                curr_prog = p_obj
            else:
                if str(raw_name).lower() == 'total':
                    curr_prog = None
                else: 
                     # print(f"  AVISO: Programa não mapeado: {raw_sigla} / {raw_code}")
                     curr_prog = None
        
        if not curr_prog:
            continue
            
        # 2. Process Agency
        if c_agency >= len(row): continue
        agencia_raw = row.iloc[c_agency]
        
        if pd.isna(agencia_raw): continue
        if str(agencia_raw).lower() == 'total': continue
            
        agencia = resolve_agencia(agencia_raw, agencias_db)
        if not agencia: continue
            
        # 3. Read Years
        # Years are consecutive from c_year_start
        # 2014 is at c_year_start
        for i in range(12): # 2014 to 2025 = 12 years
            ano = 2014 + i
            col_idx = c_year_start + i
            
            if col_idx < len(row):
                val = row.iloc[col_idx]
                try:
                    val_float = float(val)
                    if pd.isna(val_float): val_float = 0
                    qtd = int(val_float)
                except:
                    qtd = 0
                
                if curr_prog.sigla_programa == 'PPGEQ':
                    with open("debug_ppgeq_import.txt", "a", encoding="utf-8") as f:
                        f.write(f"DEBUG PPGEQ: Ano={ano} Col={col_idx} Val={val} -> Qtd={qtd} Agency={agencia.sigla}\n")
                
                if qtd > 0:
                    key = (ano, curr_prog.id, agencia.id)
                    stats_buffer[key] = stats_buffer.get(key, 0) + qtd

    # 4. Commit
    print(f"  Salvando {len(stats_buffer)} registros calculados no banco...")
    count = 0
    for key, qtd in stats_buffer.items():
        ano, prog_id, ag_id = key
        
        vol = BolsaVolumetriaAnual(
            ano_referencia=ano,
            programa_id=prog_id,
            agencia_id=ag_id,
            nivel=level,
            qtd_sistema=qtd,
            qtd_manual_extra=0
        )
        db.session.add(vol)
        count += 1
        
    db.session.commit()
    print(f"  {level}: {count} inserts realizados com sucesso.")


def run():
    print("--- INICIANDO RE-IMPORTAÇÃO HIERÁRQUICA ---")
    with app.app_context():
        # 1. Cleaning
        print("Limpando tabela BolsaVolumetriaAnual...")
        try:
            num_deleted = db.session.query(BolsaVolumetriaAnual).delete()
            db.session.commit()
            print(f"Registros removidos: {num_deleted}")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao limpar tabela: {e}")
            return

        # 2. Process Files
        process_file('Mestrado', FILES['Mestrado'])
        process_file('Doutorado', FILES['Doutorado'])

if __name__ == '__main__':
    run()
