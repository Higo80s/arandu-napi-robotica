import pandas as pd
import sys
import os
import re
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import Bolsista, Edital, Modalidade, ProgramaAcademico, AgenciaFomento
from extensions import db

def parse_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), '%d/%m/%Y').date()
    except Exception:
        return None

def import_capes():
    filepath = os.path.join("planilnhas_externas", "capes", "capes_ppg_todos_bolsistas.xlsx")
    print(f"Lendo base de dados CAPES: {filepath}")
    
    df = pd.read_excel(filepath)
    hoje = datetime.now().date()
    
    with app.app_context():
        # Busca os Editais Base
        edital_ppg = Edital.query.filter_by(numero="CAPES PPG").first()
        edital_ies = Edital.query.filter_by(numero="CAPES (IES) PROPPG").first()
        
        if not edital_ppg or not edital_ies:
            print("Erro: Editais 'CAPES PPG' ou 'CAPES (IES) PROPPG' não encontrados.")
            return
            
        # Pega/Cria modalidades padrões para evitar erros
        def get_modalidade(edital, nivel):
            mod = Modalidade.query.filter_by(edital_id=edital.id, nivel=nivel).first()
            if not mod:
                val = 2100.0 if nivel == 'Mestrado' else 3100.0
                mod = Modalidade(edital_id=edital.id, nivel=nivel, vagas=999, valor_mensal=val, max_meses=24 if nivel == 'Mestrado' else 48)
                db.session.add(mod)
                db.session.commit()
            return mod

        # Busca programas em cache para velocidade
        programas_cache = {p.codigo_programa: p.id for p in ProgramaAcademico.query.all()}
        
        count_inserted = 0
        count_updated = 0
        count_skipped = 0
        
        for index, row in df.iterrows():
            tipo_vinculo = str(row.get('Tipo Vínculo', ''))
            beneficiario = str(row.get('Beneficiário', ''))
            vigencia = str(row.get('Vigência', ''))
            situacao = str(row.get('Situação', ''))
            nivel_modalidade = str(row.get('Modalidade', ''))
            
            if pd.isna(beneficiario) or beneficiario == 'nan':
                continue
            
            # 1. Definir Edital (Regra de Negócio)
            edital_destino = edital_ppg
            if "Discente IES Participante" in tipo_vinculo:
                edital_destino = edital_ies
                
            # 2. Extrair Programa
            programa_id = None
            vinculo_parts = tipo_vinculo.split(' - ')
            if len(vinculo_parts) >= 2:
                codigo_sucupira = vinculo_parts[1].strip()
                programa_id = programas_cache.get(codigo_sucupira)
                
            # 3. Extrair Nome e CPF provisório
            ben_parts = beneficiario.split(' - ', 1)
            cpf_prov = ben_parts[0].strip() if len(ben_parts) > 0 else '000.000.000-00'
            nome = ben_parts[1].strip() if len(ben_parts) > 1 else 'NOME DESCONHECIDO'
            
            # 4. Vigência
            vig_parts = vigencia.split(' - ')
            start_date = None
            end_date = None
            if len(vig_parts) == 2:
                start_date = parse_date(vig_parts[0])
                end_date = parse_date(vig_parts[1])
                
            if not start_date or not end_date:
                count_skipped += 1
                continue
                
            # 5. Status Ativo
            ativo = False
            if 'Em acompanhamento' in situacao:
                ativo = True
                
            # Duração em meses (aproximada, usando regra simples)
            meses_duracao = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
            if end_date.day > start_date.day:
                meses_duracao += 1
            if meses_duracao <= 0:
                meses_duracao = 1
                
            # 6. Modalidade
            mod = get_modalidade(edital_destino, nivel_modalidade)
            
            # Validação se existe
            # NOTA: O CPF tá ofuscado, então pode haver colisão se houverem várias pessoas com o mesmo padrão "***.123.456-**".
            # Vamos buscar por nome e data de início para evitar duplicidade.
            existente = Bolsista.query.filter_by(
                nome=nome,
                edital_id=edital_destino.id,
                data_inicio_bolsa=start_date
            ).first()
            
            if existente:
                # Update status
                if existente.ativo != ativo or existente.data_fim_bolsa != end_date:
                    existente.ativo = ativo
                    existente.data_fim_bolsa = end_date
                    count_updated += 1
            else:
                # Create
                novo = Bolsista(
                    nome=nome,
                    cpf=cpf_prov, # Ofuscado, editado depois
                    edital_id=edital_destino.id,
                    modalidade_id=mod.id,
                    programa_id=programa_id,
                    data_inicio_bolsa=start_date,
                    data_fim_bolsa=end_date,
                    meses_duracao=meses_duracao,
                    ativo=ativo
                )
                db.session.add(novo)
                count_inserted += 1
                
        db.session.commit()
        print(f"Concluído! Inseridos: {count_inserted} | Atualizados: {count_updated} | Ignorados: {count_skipped}")

if __name__ == "__main__":
    import_capes()
