import pandas as pd
import os

FILE_PATH = r"planilnhas_externas/UTFPR_Consolidado_Gestao_Com_Agencias (1).xlsx"

def run():
    print("--- ANALISE DE DUPLICATAS ---")
    if not os.path.exists(FILE_PATH):
        print("Arquivo não encontrado.")
        return

    df = pd.read_excel(FILE_PATH)
    print(f"Total Lines: {len(df)}")
    
    # Check duplicates in Code STRIPPED
    df['Code_Clean'] = df['Código CAPES'].astype(str).str.strip()
    dup_counts = df['Code_Clean'].value_counts()
    dups = dup_counts[dup_counts > 1]
    
    print(f"Códigos Duplicados (Stripped): {len(dups)}")
    
    for code, count in dups.items():
        print(f"\nCode: '{code}' (Count: {count})")
        rows = df[df['Code_Clean'] == code]
        for idx, row in rows.iterrows():
            print(f"  Row {idx}: Nome='{row['Nome do Programa']}' Campus='{row.get('Campus')}' Tipo='{row.get('Tipo')}'")
            # Print other potential level columns?
            # Let's print the first 10 values
            # print(row.values[:10])

if __name__ == '__main__':
    run()
