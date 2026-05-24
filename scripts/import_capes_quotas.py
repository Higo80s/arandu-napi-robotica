
import sqlite3
import os
import re
import unicodedata

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "instance", "gestao_editais_new.db")
# Using the test file located in lab for now, or I should expect it in root?
# I will read from tests/quotas_lab/capes_data.txt as source since user didn't upload a new one.
DATA_PATH = os.path.join(BASE_DIR, "tests", "quotas_lab", "capes_data.txt")

EDITAL_TARGET_ID = 14 # CAPES DS

def normalize_key(text):
    if not text: return ""
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    return text.upper().strip()

def run_import():
    print(f"Starting Import... DB: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("DB Not Found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Fetch Modalidades
    cursor.execute("SELECT id, nivel FROM modalidades WHERE edital_id=?", (EDITAL_TARGET_ID,))
    mods = cursor.fetchall()
    mod_map = {}
    for mid, nivel in mods:
        if 'MESTRADO' in nivel.upper(): mod_map['Mestrado'] = mid
        if 'DOUTORADO' in nivel.upper(): mod_map['Doutorado'] = mid
        
    print(f"Modalidades: {mod_map}")
    
    # 2. Load Programs (Map by Code AND Name)
    cursor.execute("SELECT id, nome_programa, codigo_programa FROM programa_academico")
    db_programs = cursor.fetchall()
    
    prog_map_name = {}
    prog_map_code = {}
    
    for pid, pnome, pcode in db_programs:
        # Name Map
        key = normalize_key(pnome)
        entry = {'id': pid, 'code': pcode, 'name': pnome}
        prog_map_name[key] = entry
        
        # Code Map
        if pcode:
            prog_map_code[pcode.strip().upper()] = entry
            
    print(f"Loaded {len(db_programs)} programs.")
    
    # 3. Process File
    if not os.path.exists(DATA_PATH):
        print("Data file missing.")
        return
        
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    success = 0
    updated_codes = 0
    failures = 0
    
    for line in lines:
        parts = line.strip().split('\t')
        if len(parts) < 8: continue
        
        nivel_raw = parts[2].strip()
        prog_raw = parts[4].strip()
        qtd_conc = int(parts[5])
        qtd_util = int(parts[6])
        qtd_disp = int(parts[7])
        
        if "Discente IES" in prog_raw: continue
        
        match = re.match(r'^([0-9A-Z]+)\s+-\s+(.+)$', prog_raw)
        if not match: continue
        
        code_capes = match.group(1).strip().upper()
        name_capes = match.group(2).strip()
        norm_capes = normalize_key(name_capes)
        
        target_prog = None
        
        # Priority 1: Match by Code
        if code_capes in prog_map_code:
            target_prog = prog_map_code[code_capes]
            # print(f"Matched by Code: {code_capes}")
            
        # Priority 2: Match by Name (Exact)
        elif norm_capes in prog_map_name:
            target_prog = prog_map_name[norm_capes]
            
        # Priority 3: Fuzzy Name
        else:
            for db_key, db_val in prog_map_name.items():
                if db_key in norm_capes or norm_capes in db_key:
                    if abs(len(db_key) - len(norm_capes)) < 12: # Relaxed heuristic
                        target_prog = db_val
                        print(f"Fuzzy Match: '{name_capes}' -> '{db_val['name']}'")
                        break
        
        if target_prog:
            # Update Code if missing in DB
            if not target_prog['code']:
                try:
                    cursor.execute("UPDATE programa_academico SET codigo_programa = ? WHERE id = ?", (code_capes, target_prog['id']))
                    updated_codes += 1
                except Exception as e:
                    print(f"Update Error: {e}")
            
            # Insert Quota
            mod_id = mod_map.get(nivel_raw)
            if mod_id:
                cursor.execute("DELETE FROM distribuicao_cotas WHERE programa_id=? AND modalidade_id=?", (target_prog['id'], mod_id))
                cursor.execute("""
                    INSERT INTO distribuicao_cotas (edital_id, programa_id, modalidade_id, qtd_concedida, qtd_utilizada_capes, qtd_disponivel_capes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (EDITAL_TARGET_ID, target_prog['id'], mod_id, qtd_conc, qtd_util, qtd_disp))
                success += 1
        else:
            print(f"FAILED TO MATCH: {code_capes} - {name_capes}")
            failures += 1
            
    conn.commit()
    print(f"Import Finished. Quotas Set: {success}. Codes Updated: {updated_codes}. Failures: {failures}.")
    conn.close()

if __name__ == "__main__":
    run_import()
