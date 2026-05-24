import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "instance", "gestao_editais_new.db")

PROFESSIONAL_CODES = [
    "31001017169P2", # Sim (Mestrado Profissional em Rede) 
    "31075010001P2", # Sim (Mestrado Profissional em Rede) 
    "31102000001P6", # Sim (Mestrado Profissional em Rede) 
    "33004013069P2", # Sim (Mestrado Profissional em Rede) 
    "33283010001P5", # Sim (Mestrado Profissional em Rede) 
    "40006018006P3", # Sim (Mestrado Profissional) 
    "40006018011P7", # Sim (Mestrado Profissional) 
    "40006018015P2", # Sim (Mestrado Profissional) 
    "40006018017P5", # Sim (Mestrado e Doutorado Profissional) 
    "40006018018P1", # Sim (Mestrado Profissional) 
    "40006018019P8", # Sim (Mestrado e Doutorado Profissional) 
    "40006018025P8", # Sim (Mestrado Profissional) 
    "40006018027P0", # Sim (Mestrado Profissional) 
    "40006018034P7", # Sim (Mestrado Profissional) 
    "40006018038P2", # Sim (Mestrado Profissional) 
    "40006018041P3", # Sim (Mestrado Profissional) 
    "40006018170P8", # Sim (Mestrado Profissional) 
    "40006018180P3", # Sim (Mestrado Profissional) 
    "53045009001P3", # Sim (Mestrado Profissional em Rede) 
]

def update_professional_status():
    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Resetting all programs to 'Acadêmico'...")
    cursor.execute("UPDATE programa_academico SET tipo_oferta = 'Acadêmico'")
    
    print(f"Updating {len(PROFESSIONAL_CODES)} programs to 'Profissional'...")
    
    placeholders = ','.join(['?'] * len(PROFESSIONAL_CODES))
    query = f"UPDATE programa_academico SET tipo_oferta = 'Profissional' WHERE codigo_programa IN ({placeholders})"
    
    cursor.execute(query, PROFESSIONAL_CODES)
    updated_count = cursor.rowcount
    
    print(f"Updated {updated_count} rows.")
    
    # Verify
    print("\n--- Verification ---")
    rows = cursor.execute("SELECT codigo_programa, nome_programa, campus_id, tipo_oferta FROM programa_academico WHERE tipo_oferta = 'Profissional'").fetchall()
    
    # Get campus names
    campus_rows = cursor.execute("SELECT id, sigla_campus FROM campus").fetchall()
    campus_map = {c[0]: c[1] for c in campus_rows}

    print(f"Found {len(rows)} professional programs in DB:")
    for r in rows:
        campus = campus_map.get(r[2], 'UNKNOWN')
        print(f"[{r[0]}] {r[1]} ({campus}) - {r[3]}")
        
    conn.commit()
    conn.close()
    print("\nUpdate complete.")

if __name__ == "__main__":
    update_professional_status()
