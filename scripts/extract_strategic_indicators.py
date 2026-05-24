
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, Residente, Campus, ProgramaAcademico
from sqlalchemy import func
from datetime import datetime
import pandas as pd

def extract_indicators():
    with app.app_context():
        print(f"=== INDICADORES ESTRATÉGICOS: RESIDENTES PÓS-DOC ===")
        print(f"Data de Extração: {datetime.now().strftime('%d/%m/%Y')}\n")

        # Query na tabela específica de Residentes
        query = db.session.query(Residente).all()
        
        total_residentes = len(query)
        print(f"Total de Residentes Cadastrados: {total_residentes}")
        
        if total_residentes == 0:
            print("Nenhum residente encontrado na tabela dedicada.")
            return

        df_data = []
        for r in query:
            # Lógica para obter Campus e Programa
            campus_nome = 'N/A'
            programa_nome = 'N/A'
            
            if r.programa_link:
                programa_nome = r.programa_link.nome_programa
                if r.programa_link.campus:
                    campus_nome = r.programa_link.campus.nome
            elif r.modalidade and r.modalidade.edital: # Fallback se não tiver link direto
                 # Tenta inferir do edital se possível, mas geralmente PósDoc é vinculado a programa
                 pass

            df_data.append({
                'Campus': campus_nome,
                'Programa': programa_nome,
                'Inicio': r.data_inicio,
                'Duracao_Meses': r.meses_duracao,
                'Ano_Ingresso': r.data_inicio.year if r.data_inicio else None,
                'Recebe_Bolsa': r.recebe_bolsa,
                'Agencia': r.agencia_fomento if r.agencia_fomento else 'Não Informada'
            })
            
        df = pd.DataFrame(df_data)
        
        # 1. Distribuição Geográfica (Campus) e Acadêmica (Programa)
        print("\n--- DISTRIBUIÇÃO POR CAMPUS ---")
        print(df['Campus'].value_counts().to_string())
        
        print("\n--- TOP 5 PROGRAMAS (INTERESSE) ---")
        print(df['Programa'].value_counts().head(5).to_string())

        # 2. Tempo Médio de Permanência
        print("\n--- TEMPO MÉDIO DE ESTÁGIO (MESES) ---")
        if 'Duracao_Meses' in df and not df['Duracao_Meses'].isnull().all():
            avg_time = df['Duracao_Meses'].mean()
            print(f"Média Geral: {avg_time:.1f} meses")
        else:
             print("Dados de duração insuficientes.")
        
        # 3. Evolução Anual (Novos Cadastros)
        print("\n--- EVOLUÇÃO TEMPORAL (NOVOS RESIDENTES/ANO) ---")
        if 'Ano_Ingresso' in df and not df['Ano_Ingresso'].isnull().all():
            evo = df.groupby('Ano_Ingresso').size().reset_index(name='Qtd')
            # Converte ano para int para tirar casa decimal
            evo['Ano_Ingresso'] = evo['Ano_Ingresso'].astype(int)
            print(evo.to_string(index=False))
        
        # 4. Perfil de Financiamento (Transparência)
        print("\n--- PERFIL DE FINANCIAMENTO ---")
        df['Status'] = df['Recebe_Bolsa'].apply(lambda x: 'Bolsista' if x else 'Voluntário')
        print(df['Status'].value_counts().to_string())
        
        print("\n--- AGÊNCIAS DE FOMENTO CITADAS ---")
        print(df['Agencia'].value_counts().head(5).to_string())

if __name__ == "__main__":
    extract_indicators()
