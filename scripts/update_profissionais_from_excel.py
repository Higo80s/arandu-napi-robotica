import os
import sys
import pandas as pd
from app import app, db
from models import ProgramaAcademico, Bolsista, Edital

FILE_PATH = r"c:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo\planilnhas_externas\RG 2025 Programas de pós-graduação por câmpus.xlsx"

def update_professional_programs():
    print("Iniciando a verificação de Programas Profissionais usando a planilha de 2025...")
    if not os.path.exists(FILE_PATH):
        print(f"Erro: Arquivo não encontrado em {FILE_PATH}")
        return

    try:
        df = pd.read_excel(FILE_PATH)
    except Exception as e:
        print(f"Erro ao ler excel: {e}")
        return

    # Assuming the spreadsheet has columns like 'Sigla', 'Tipo', 'Nome', etc.
    # Let's verify the columns first
    print(f"Colunas encontradas: {df.columns.tolist()}")

    with app.app_context():
        updated_count = 0
        
        # Iterate over df. Assuming 'Sigla do Programa' or 'Programa' and 'Nível' or 'Tipo' exists.
        # We need to map it back to `ProgramaAcademico.sigla_programa`
        # Since I don't know the exact columns, let's try to infer or print them if they mismatch.

        # Hardcoding mapped columns based on the printed output
        col_sigla = 'Sigla'
        col_tipo = 'Nivel'
                
        if col_sigla in df.columns and col_tipo in df.columns:
            print(f"Usando colunas: Sigla='{col_sigla}', Tipo='{col_tipo}'")
            for index, row in df.iterrows():
                sigla = str(row[col_sigla]).strip()
                tipo_val = str(row[col_tipo]).strip()
                
                # Check if it's professional
                if 'profissional' in tipo_val.lower():
                    # Find in DB
                    prog = ProgramaAcademico.query.filter(ProgramaAcademico.sigla_programa.ilike(sigla)).first()
                    if prog:
                        if prog.tipo_oferta != 'Profissional':
                            prog.tipo_oferta = 'Profissional'
                            updated_count += 1
                            print(f"[ATUALIZADO] {sigla}: Marcado como Profissional.")
                    else:
                        print(f"[AVISO] Programa Profissional '{sigla}' não encontrado no banco de dados.")
                        
            db.session.commit()
            print(f"Concluído. {updated_count} programas atualizados para Profissional.")
        else:
            print("Não foi possível inferir as colunas de Sigla e Tipo automaticamente. Por favor, verifique as colunas impressas acima.")

        # Bonus UI check: let's also update the "Agência P&D" mapping requested by the user.
        # This will be done in the template, but we can check if they exist here.
        
if __name__ == '__main__':
    update_professional_programs()
