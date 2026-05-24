import sqlite3
import os
import pandas as pd

# Setup DB path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "instance", "gestao_editais_new.db")

# 1. Official Data (New/Updates)
NEW_PROGRAMS = [
    # (Code, Name, Sigla, CampusSigla, Level, AreaAv, AreaBasic, Year, Grade)
    ("40006018185P5", "Educação Tecnológica", "PPGET", "CT", "M", "Educação", "Educação", 2025, "A"),
    ("40006018184P9", "Design Prospectivo", "PPGDP", "CT", "M", "Arquitetura, Urbanismo e Design", "Design", 2025, "A"),
    ("40006018031P8", "Engenharia de Produção e Sistemas", "PPGEPS", "CT", "D", "ENGENHARIAS III", "ENGENHARIA DE PRODUÇÃO", 2025, "4"), # Multicampi Expansion
    ("TEMP_CC_TD_2025", "Ciência da Computação", "PPGCC", "TD", "M", "CIÊNCIA DA COMPUTAÇÃO", "CIÊNCIA DA COMPUTAÇÃO", 2025, "3"), # Placeholder Code
    ("33283010001P5", "Ensino de Física - PROFIS (Polo)", "DNPEF", "CM", "DP", "ASTRONOMIA / FÍSICA", "FÍSICA", 2025, "5"),
]

LEVEL_UPDATES = [
    # (Sigla, CampusSigla, NewLevels)
    ("PPGBIOTEC", "PG", "M, D"),
    ("PPGBIOTEC", "DV", "M, D"), # Multicampi
    ("PPGZO", "DV", "M, D"),
    ("PPGTA", "MD", "M, D"),
    ("PPGTA", "CM", "M, D"), # Multicampi
    ("PPGEPS", "PB", "M, D"), # Note: Already Doutorado approval mentioned, ensure PB also reflects M, D
    ("PPGEPS", "CT", "M, D"), # Ensure CT reflects M, D
    ("PPGCTA", "CT", "M, D"), # From previous context
    ("PPGEC", "CT", "M, D"),  # From previous context
    ("CPGEI", "CT", "M, D"),  # From previous context
    ("PPGEM", "CT", "M, D"),  # From previous context
    ("PPGFCET", "CT", "MP, DP"), # From previous context
    ("PPGPGP", "CT", "MP, DP"), # From previous context
    ("PPGTE", "CT", "M, D"),  # From previous context
    ("PPGZO", "DV", "M, D"),  # From previous context
    ("PPGTA", "MD", "M, D"),  # From previous context
    ("PPGTA", "CM", "M, D"),  # From previous context
    ("PPGAG", "PB", "M, D"),  # From previous context
    ("PPGDR", "PB", "M, D"),  # From previous context
    ("PPGEP", "PG", "M, D"),  # From previous context
    ("PPGECT", "PG", "MP, D"), # From previous context check (MP, D or MP, DP?) usually MP/D for acad/prof mix
]

NOTE_UPDATES = [
    ("CPGEI", "CT", "7"),
    ("PPGTE", "CT", "6")
]

def update_ppg():
    print("Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 0. Load Campus Map
    campuses = cursor.execute("SELECT id, sigla_campus FROM campus").fetchall()
    campus_map = {c['sigla_campus']: c['id'] for c in campuses}
    
    # 1. Insert/Update New Programs
    print("\n--- Processing New Programs ---")
    for prog in NEW_PROGRAMS:
        code, name, sigla, campus_sigla, level_abbr, area_av, area_b, year, grade = prog
        
        if campus_sigla not in campus_map:
            print(f"ERROR: Campus {campus_sigla} not found for {name}")
            continue
            
        campus_id = campus_map[campus_sigla]
        
        # Check if exists
        existing = cursor.execute(
            "SELECT id, niveis FROM programa_academico WHERE (codigo_programa = ? OR sigla_programa = ?) AND campus_id = ?",
            (code, sigla, campus_id)
        ).fetchone()

        if existing:
            print(f"Updating existing program: {name} ({campus_sigla})")
            # Update info
            cursor.execute("""
                UPDATE programa_academico 
                SET nome_programa = ?, sigla_programa = ?, area_avaliacao = ?, area_basica = ?, ano_inicio = min(ano_inicio, ?), nota_capes = ?
                WHERE id = ?
            """, (name, sigla, area_av, area_b, year, grade, existing['id']))
            
            # Update levels logic (append D if not present)
            current_levels = existing['niveis'] or ""
            if level_abbr not in current_levels:
                new_levels = current_levels + ", " + level_abbr if current_levels else level_abbr
                cursor.execute("UPDATE programa_academico SET niveis = ? WHERE id = ?", (new_levels, existing['id']))

        else:
            print(f"Inserting NEW program: {name} ({campus_sigla})")
            cursor.execute("""
                INSERT INTO programa_academico (codigo_programa, nome_programa, sigla_programa, campus_id, niveis, area_avaliacao, area_basica, ano_inicio, nota_capes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (code, name, sigla, campus_id, level_abbr, area_av, area_b, year, grade))

    # 2. Update Levels Explicitly
    print("\n--- Updating Levels ---")
    for sigla, campus_sigla, new_levels in LEVEL_UPDATES:
        if campus_sigla in campus_map:
            campus_id = campus_map[campus_sigla]
            cursor.execute("UPDATE programa_academico SET niveis = ? WHERE sigla_programa = ? AND campus_id = ?", (new_levels, sigla, campus_id))
            if cursor.rowcount > 0:
                print(f"Updated levels for {sigla} ({campus_sigla}) to {new_levels}")
            else:
                 # Try finding by partial name if sigla fails
                 pass

    # 3. Update Notes
    print("\n--- Updating Notes ---")
    for sigla, campus_sigla, new_note in NOTE_UPDATES:
        if campus_sigla in campus_map:
            campus_id = campus_map[campus_sigla]
            cursor.execute("UPDATE programa_academico SET nota_capes = ? WHERE sigla_programa = ? AND campus_id = ?", (new_note, sigla, campus_id))
            print(f"Updated note for {sigla} ({campus_sigla}) to {new_note}")

    # 4. Check Aeroespacial
    print("\n--- Checking Aerospace Engineering ---")
    aero = cursor.execute("SELECT * FROM programa_academico WHERE nome_programa LIKE '%Aeroespacial%'").fetchall()
    if not aero:
        print("WARNING: Engenharia Aeroespacial NOT FOUND in database.")
    else:
        for a in aero:
            ts = [k for k,v in campus_map.items() if v == a['campus_id']][0]
            print(f"FOUND: {a['nome_programa']} ({ts}) - Levels: {a['niveis']}")

    conn.commit()
    
    # 5. Generate Final Report
    print("\n--- Consolidated 2025 Report ---")
    query = """
        SELECT 
            p.codigo_programa as Code, 
            p.nome_programa as Name, 
            c.sigla_campus as Campus, 
            p.niveis as Levels, 
            p.nota_capes as Grade
        FROM programa_academico p
        JOIN campus c ON p.campus_id = c.id
        ORDER BY p.nome_programa, c.sigla_campus
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    # Save to file
    report_path = os.path.join(BASE_DIR, "docs", "RELATORIO_PPG_2025.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(df.to_string(index=False))
    print(f"\nReport saved to {report_path}")

    conn.close()

if __name__ == "__main__":
    update_ppg()
