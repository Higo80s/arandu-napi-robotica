import sys
import os
import pandas as pd

# Contexto da Aplicação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import ProgramaAcademico, Campus

def run():
    print("Iniciando exportação de Programas Acadêmicos...")
    with app.app_context():
        # Querying data
        programs = db.session.query(ProgramaAcademico).all()
        
        data = []
        for p in programs:
            campus_nome = p.campus.nome if p.campus else "N/A"
            campus_sigla = p.campus.sigla_campus if p.campus else "N/A"
            
            data.append({
                'ID': p.id,
                'Código Programa (CAPES)': p.codigo_programa,
                'Sigla': p.sigla_programa,
                'Nome do Programa': p.nome_programa,
                'Campus': campus_nome,
                'Sigla Campus': campus_sigla,
                'Nota CAPES': p.nota_capes,
                'Área de Avaliação': p.area_avaliacao,
                'Área Básica': p.area_basica,
                'Ano Início': p.ano_inicio,
                'Níveis Ofertados': p.niveis,
                'Tipo Oferta': p.tipo_oferta
            })
            
        df = pd.DataFrame(data)
        
        # Sort by Campus then Program Name
        df = df.sort_values(by=['Campus', 'Nome do Programa'])
        
        output_file = "consolidado_programas_utfpr.xlsx"
        df.to_excel(output_file, index=False)
        print(f"Sucesso! Arquivo gerado: {os.path.abspath(output_file)}")
        print(f"Total de registros exportados: {len(df)}")

if __name__ == '__main__':
    run()
