import pandas as pd
import sys
import os

def explore_capes_sheets():
    folder = "planilnhas_externas/capes"
    files = [
        "capes_Lista de Concessões.xlsx",
        "capes_cotas.xlsx",
        "capes_cotas_ppg.xlsx",
        "capes_ies.xlsx",
        "capes_ppg_todos_bolsistas.xlsx"
    ]
    
    for filename in files:
        filepath = os.path.join(folder, filename)
        if os.path.exists(filepath):
            print(f"--- Ficheiro: {filename} ---")
            try:
                df = pd.read_excel(filepath)
                print("Count:", len(df))
                print("Columns:", list(df.columns))
                if len(df) > 0:
                    print("Sample row 0:")
                    print(df.iloc[0].to_dict())
            except Exception as e:
                print(f"Erro ao ler {filename}: {e}")
            print("\n")

if __name__ == "__main__":
    explore_capes_sheets()
