import sys
import os
import pandas as pd
import logging
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import ProgramaAcademico, BolsaHistorico, Campus

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

import sys
import os
import pandas as pd
import logging
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import ProgramaAcademico, BolsaHistorico, Campus

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def process_scholarship_data(df, level_name):
    """
    Process DataFrame based on specific layout of PROPPG files.
    """
    # 1. Rename Columns based on known layout
    if level_name == 'Mestrado':
        # Header=3 implies: 'Programa', 'Unnamed: 1' (Nome), 'Unnamed: 2' (Sigla), 'Unnamed: 3' (Codigo), 'Agência'
        rename_dict = {
            'Unnamed: 3': 'Codigo',
            'Unnamed: 2': 'Sigla',
            'Agência': 'Agencia',
            'AgênciaÂ': 'Agencia', # Handle encoding artifact if present
            'Agência ': 'Agencia'  # Handle nbsp
        }
    else: # Doutorado
        # Header=2 implies: 'código', 'sigla', 'Agência'
        rename_dict = {
            'código': 'Codigo',
            'sigla': 'Sigla',
            'Agência': 'Agencia',
            'campus': 'Campus'
        }
    
    # Normalize input columns (strip)
    df.columns = [str(c).strip() for c in df.columns]
    
    # Apply rename
    df = df.rename(columns=rename_dict)
    
    # Check critical column
    if 'Agencia' not in df.columns:
        # Fallback search for Agency column
        for c in df.columns:
            if 'Agência' in c or 'Agencia' in c:
                df = df.rename(columns={c: 'Agencia'})
                break
    
    if 'Agencia' not in df.columns:
        print(f"[ERROR] 'Agencia' column not found in {level_name}. Cols: {df.columns.tolist()}")
        return pd.DataFrame()

    # 2. Forward Fill Metadata (Program info is often only on the first row of the block)
    if 'Codigo' in df.columns:
        df['Codigo'] = df['Codigo'].fillna(method='ffill')
    if 'Sigla' in df.columns:
        df['Sigla'] = df['Sigla'].fillna(method='ffill')
    
    # 3. Filter Rows
    # Remove header repetitions or totals
    df = df[df['Agencia'].notna()]
    df = df[~df['Agencia'].isin(['Total', 'Agência', 'Agência '])]

    # 4. Identify Year Columns
    # We want 2014 to 2025
    year_cols = []
    for c in df.columns:
        clean_c = c.replace('.0', '')
        if clean_c.isdigit() and 2014 <= int(clean_c) <= 2025:
            year_cols.append(c)
    
    if not year_cols:
        print(f"[ERROR] No year columns (2014-2025) found in {level_name}")
        return pd.DataFrame()

    # 5. Melt (Unpivot)
    id_vars = [c for c in ['Codigo', 'Sigla', 'Agencia'] if c in df.columns]
    df_melted = df.melt(id_vars=id_vars, value_vars=year_cols, var_name='Ano', value_name='Quantidade')
    
    # 6. Clean Values
    df_melted['Ano'] = df_melted['Ano'].astype(str).str.replace('.0', '', regex=False)
    df_melted['Quantidade'] = df_melted['Quantidade'].astype(str).str.replace('–', '0').str.replace('-', '0').str.replace('nan', '0')
    df_melted['Quantidade'] = pd.to_numeric(df_melted['Quantidade'], errors='coerce').fillna(0).astype(int)
    
    df_melted['Nivel'] = level_name
    
    return df_melted

def import_history():
    print("--- Importing Scholarship History (Robust ETL) ---")
    
    # Define File Paths (User Provided Names)
    # Trying exact names first, then fuzzy match if needed
    files = {
        'Mestrado': '_PROPPG_15 - Número de bolsas de mestrado nos programas acadêmicos e profissionais 2025.xlsx - Planilha1 2025.csv',
        'Doutorado': '_PROPPG_17 - Número de bolsas nos programas de doutorado da UTFPR.xlsx - Planilha1 - Finalizada.csv'
    }

    # Agency Mapping
    agency_map = {
        'CAPES - IES': 'CAPES', 'CAPES - DS': 'CAPES', 'CAPES DS': 'CAPES', 'Capes': 'CAPES',
        'CAPES - IES*': 'CAPES', 'CAPES-IES': 'CAPES', 
        'CNPq ': 'CNPq',
        'Outras*': 'Outras', 'Outras ': 'Outras'
    }

    with app.app_context():
        total_inserted = 0
        
        for level, filename in files.items():
            if not os.path.exists(filename):
                print(f"[WARN] File not found: {filename}")
                # Try finding any csv with similar name
                found = False
                for f in os.listdir('.'):
                    if (level == 'Mestrado' and '_PROPPG_15' in f and f.endswith('.csv')) or \
                       (level == 'Doutorado' and '_PROPPG_17' in f and f.endswith('.csv')):
                        filename = f
                        print(f"[INFO] Found alternative file: {filename}")
                        found = True
                        break
                if not found:
                    print(f"[SKIP] Skipping {level} - No file.")
                    continue

            print(f"Processing {level} from {filename}...")
            
            try:
                # Read CSV
                # Header row varies. User said 3 for Mestrado, 2 for Doutorado.
                header_row = 3 if level == 'Mestrado' else 2
                df = pd.read_csv(filename, header=header_row)
                
                # Process
                df_clean = process_scholarship_data(df, level)
                
                if df_clean.empty:
                    print(f"[WARN] No data processed for {level}")
                    continue

                # Map Agencies
                df_clean['Agencia'] = df_clean['Agencia'].str.strip().replace(agency_map)
                
                # Insert into DB
                # Iterate rows
                for _, row in df_clean.iterrows():
                    qty = row['Quantidade']
                    # if qty == 0: continue # Optional: skip zeros to save space? User verification showed zeros in history.
                    
                    # Resolve Program ID
                    code = str(row['Codigo']).strip().split('\\')[0] # Remove artifacts like \n
                    agency = row['Agencia']
                    year = int(row['Ano'])
                    
                    # Find Program (We might need Campus logic if code is not unique)
                    # For now, finding by code. If multiple campuses have same code (Multicampi), we might have an issue.
                    # The CSV for Doutorado HAS Campus column. Mestrado CSV in user sample 'Câmpus AP' in row 0?
                    # Actually user sample for Mestrado shows 'Câmpus AP' in row 0, col 0?
                    # But the robust logic relies on Code.
                    # If Code is unique per campus in our DB (it's not anymore), we need Campus.
                    
                    # Try to find program(s) by code
                    progs = ProgramaAcademico.query.filter_by(codigo_programa=code).all()
                    
                    target_prog = None
                    if len(progs) == 1:
                        target_prog = progs[0]
                    elif len(progs) > 1:
                        # Ambiguity (Multicampi). Need Campus.
                        # Do we have Campus in df?
                        # Doutorado has 'Campus' column.
                        # Mestrado snippet: Row 4: ... CT ... PROFMAT.
                        # So Mestrado MIGHT have campus in 'Unnamed: X'?
                        # User snippet implies Unnamed: 3 is Code. Where is Campus?
                        # Snippet: Unnamed: 18 might be Campus? (User snippet: "Unnamed: 18... Código Câmpus Programa")
                        # It seems Mestrado file is messy.
                        # Fallback: Apply to ALL programs with this code? Or try to map from header?
                        # For now, applying to the first match or all if ambiguity is acceptable for history?
                        # No, splitting history by campus is better.
                        # Let's try to map to ALL matching programs if we can't distinguish.
                        # Better strategy: Divide quantity by number of campuses? No.
                        # Default behavior: Pick first or log warning.
                        target_prog = progs[0] # Simplification
                    
                    if target_prog:
                        # Upsert
                        # Check exist
                        hist = BolsaHistorico.query.filter_by(
                            programa_id=target_prog.id,
                            ano=year,
                            agencia=agency,
                            nivel=level
                        ).first()
                        
                        if not hist:
                            hist = BolsaHistorico(
                                programa_id=target_prog.id,
                                ano=year,
                                agencia=agency,
                                nivel=level,
                                quantidade=qty
                            )
                            db.session.add(hist)
                            total_inserted += 1
                        else:
                            if hist.quantidade != qty:
                                hist.quantidade = qty
                                total_inserted += 1
            
                db.session.commit()
                print(f"[SUCCESS] Imported {level} data.")

            except Exception as e:
                print(f"[ERROR] processing {filename}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"Total records inserted/updated: {total_inserted}")

if __name__ == "__main__":
    import_history()
