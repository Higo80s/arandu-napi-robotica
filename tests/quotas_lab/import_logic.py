
import sqlite3
import os
import re

DB_PATH = "tests/quotas_lab/quotas_test.db"
DATA_PATH = "tests/quotas_lab/capes_data.txt"

# Hardcoded Edital ID as agreed (14 = CAPES DS)
# Warning: In test DB, ID might differ if copied, but assuming 14 based on previous check.
EDITAL_TARGET_ID = 14 

def normalize_name(name):
    """Normalize string for fuzzy matching (simple uppercase trim)"""
    return name.upper().strip()

import unicodedata

def normalize_key(text):
    """Normalize text: Upper, Remove Accents, Strip"""
    if not text: return ""
    # Unicode normalize NFKD (split characters) e.g. 'á' -> 'a' + '´'
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    return text.upper().strip()

def run_import():
    if not os.path.exists(DB_PATH):
        print(f"DB not found: {DB_PATH}")
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
    
    # 2. Load ALL Programs from DB into Memory Map
    # Map: { "NORMALIZED_NAME": {id: 1, original: "Nome Real"} }
    cursor.execute("SELECT id, nome_programa, codigo_programa FROM programa_academico")
    db_programs = cursor.fetchall()
    
    prog_map = {}
    for pid, pnome, pcode in db_programs:
        key = normalize_key(pnome)
        prog_map[key] = {'id': pid, 'code': pcode, 'name': pnome}
        
    print(f"Loaded {len(prog_map)} programs from DB for matching.")
    
    # 3. Process File
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    success_count = 0
    fail_count = 0
        
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
            
        code = match.group(1)
        name_capes = match.group(2)
        norm_capes = normalize_key(name_capes)
        
        # Match Logic
        target_prog = prog_map.get(norm_capes)
        
        # Fuzzy fallback: Contains?
        if not target_prog:
            for db_key, db_val in prog_map.items():
                if db_key in norm_capes or norm_capes in db_key:
                    # Heuristic: If length diff is small, accept
                     if abs(len(db_key) - len(norm_capes)) < 10:
                        target_prog = db_val
                        print(f"Fuzzy Match: '{name_capes}' -> '{db_val['name']}'")
                        break
        
        if target_prog:
            # Update Code
            if not target_prog['code']:
                try:
                    print(f"Updating code for Program ID {target_prog['id']} to {code}")
                    cursor.execute("UPDATE programa_academico SET codigo_programa = ? WHERE id = ?", (code, target_prog['id']))
                except Exception as e:
                    print(f"UPDATE FAILED: {e}")
                    # Print columns to verify
                    cursor.execute("PRAGMA table_info(programa_academico)")
                    print([c[1] for c in cursor.fetchall()])
            
            # Insert Quota
            mod_id = mod_map.get(nivel_raw)
            if mod_id:
                try:
                    # Check duplication
                    cursor.execute("DELETE FROM distribuicao_cotas WHERE programa_id=? AND modalidade_id=?", (target_prog['id'], mod_id))
                    
                    cursor.execute("""
                        INSERT INTO distribuicao_cotas (edital_id, programa_id, modalidade_id, qtd_concedida, qtd_utilizada_capes, qtd_disponivel_capes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (EDITAL_TARGET_ID, target_prog['id'], mod_id, qtd_conc, qtd_util, qtd_disp))
                    success_count += 1
                except Exception as ex:
                    print(f"INSERT FAILED: {ex}")
        else:
            print(f"MISSING: {name_capes} (Norm: {norm_capes})")
            fail_count += 1
        
    conn.commit()
    print(f"Finished. Success: {success_count}, Failures: {fail_count}")
    conn.close()

if __name__ == "__main__":
    run_import()
