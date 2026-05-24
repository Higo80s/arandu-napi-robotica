import pandas as pd
import sys
import os

sys.path.append(os.path.abspath('.'))

from app import app
from models import Edital, Modalidade
from extensions import db

def update_capes_quotas():
    # Caminhos
    filepath_globais = os.path.join("planilnhas_externas", "capes", "capes_cotas.xlsx")
    filepath_ies = os.path.join("planilnhas_externas", "capes", "capes_ies.xlsx")
    # Nota: capes_cotas_ppg.xlsx detalha por programa, mas o limite geral para Editais é definido pelo total (PROPPG + Programas). 
    # Editais estao no DB: 13 (CAPES IES PROPPG) e 14 (CAPES PPG)

    with app.app_context():
        # Busca editais
        edital_ppg = Edital.query.filter_by(id=14).first()
        edital_ies = Edital.query.filter_by(id=13).first()

        if not edital_ppg or not edital_ies:
            print("Editais 13 ou 14 não encontrados!")
            return

        # 1. Update Edital 14 (CAPES PPG) - Cotas baseadas na capes_cotas.xlsx
        print("Lendo", filepath_globais)
        df_globais = pd.read_excel(filepath_globais)
        
        # Filtra totais globais
        mestrado_ppg_qty = df_globais[df_globais['Modalidade'] == 'Mestrado']['Qtd. Concedida'].sum()
        doutorado_ppg_qty = df_globais[df_globais['Modalidade'] == 'Doutorado']['Qtd. Concedida'].sum()
        
        # Atualiza Modalidade Mestrado PPG
        mod_m_ppg = Modalidade.query.filter_by(edital_id=14, nivel='Mestrado').first()
        if mod_m_ppg:
            mod_m_ppg.vagas = int(mestrado_ppg_qty)
            
        # Atualiza Modalidade Doutorado PPG
        mod_d_ppg = Modalidade.query.filter_by(edital_id=14, nivel='Doutorado').first()
        if mod_d_ppg:
            mod_d_ppg.vagas = int(doutorado_ppg_qty)
            
        # 2. Update Edital 13 (CAPES IES PROPPG) - Cotas baseadas na capes_ies.xlsx
        print("Lendo", filepath_ies)
        df_ies = pd.read_excel(filepath_ies)
        # O cabeçalho real usa 'Modalidade' e 'Qtd.' (Concedida) com base na nossa analise anterior.
        mestrado_ies_qty = 0
        doutorado_ies_qty = 0
        if 'Modalidade' in df_ies.columns and 'Qtd.' in df_ies.columns:
            # limpa string se necessário
            for idx, row in df_ies.iterrows():
                mod = str(row['Modalidade'])
                qtd = row['Qtd.']
                if pd.isna(qtd) or type(qtd) == str: # ignorar headers duplicados
                    continue
                if 'Mestrado' in mod:
                    mestrado_ies_qty += int(qtd)
                elif 'Doutorado' in mod:
                    doutorado_ies_qty += int(qtd)
                    
        # Atualiza Modalidade Mestrado IES
        mod_m_ies = Modalidade.query.filter_by(edital_id=13, nivel='Mestrado').first()
        if mod_m_ies:
            mod_m_ies.vagas = int(mestrado_ies_qty)
            
        # Atualiza Modalidade Doutorado IES
        mod_d_ies = Modalidade.query.filter_by(edital_id=13, nivel='Doutorado').first()
        if mod_d_ies:
            mod_d_ies.vagas = int(doutorado_ies_qty)

        db.session.commit()
        
        print("\n--- Resultados Atualizados ---")
        print(f"Edital 14 (CAPES PPG): Mestrado = {mod_m_ppg.vagas if mod_m_ppg else 0} vagas, Doutorado = {mod_d_ppg.vagas if mod_d_ppg else 0} vagas")
        print(f"Edital 13 (CAPES IES): Mestrado = {mod_m_ies.vagas if mod_m_ies else 0} vagas, Doutorado = {mod_d_ies.vagas if mod_d_ies else 0} vagas")

if __name__ == "__main__":
    update_capes_quotas()
