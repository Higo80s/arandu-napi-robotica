import sys
import os
import re
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Edital, Bolsista, Modalidade

def clean_cpf(cpf_str):
    if pd.isna(cpf_str):
        return ""
    # Remove tudo que não for número
    return re.sub(r'[^0-9]', '', str(cpf_str))

def find_or_create_edital(projeto_str):
    if not projeto_str:
        return None
        
    projeto_str_upper = projeto_str.upper()
    
    # Heurística para buscar edital existente
    # Verifica se o numero do edital bate com palavras-chave do projeto
    
    # Casos mais comuns:
    if 'RENAULT' in projeto_str_upper:
        keyword = 'RENAULT'
    elif '1756' in projeto_str_upper:
        keyword = '1756'
    elif 'SÊNIOR' in projeto_str_upper or 'SENIOR' in projeto_str_upper:
        keyword = 'SÊNIOR'
    elif 'DIKJSTRA' in projeto_str_upper:
        keyword = 'DIKJSTRA'
    else:
        # Se contiver um numero de convenio ex: 110/2025
        match = re.search(r'CONV\s*(\d{1,4}/\d{4})', projeto_str_upper)
        if match:
            keyword = match.group(1)
        else:
            keyword = projeto_str_upper[:20] # Fallback
            
    ed = Edital.query.filter(Edital.numero.ilike(f'%{keyword}%')).first()
    
    if not ed:
        # Tenta criar um novo
        ed = Edital(
            numero=f"FA - {projeto_str}",
            descricao=f"Edital gerado via planilha de pagamentos FA",
            agencia="Fundação Araucária"
        )
        db.session.add(ed)
        db.session.flush()
        print(f"  [+] Criado novo Edital ID={ed.id} baseado na keyword '{keyword}'")
        
    return ed

def run_migration():
    file_path = 'planilnhas_externas/bolsa_fa_2025_ativa.xlsm'
    try:
        df = pd.read_excel(file_path, sheet_name='pagamento', engine='openpyxl')
    except Exception as e:
        print(f"Erro ao ler a planilha: {e}")
        return
        
    # Filtra as linhas que têm nome e projeto
    df_clean = df.dropna(subset=['nome_bolsista', 'Projeto'])
    
    fixed_count = 0
    not_found_count = 0
    
    with app.app_context():
        for _, row in df_clean.iterrows():
            nome = str(row['nome_bolsista']).strip()
            cpf_raw = row['cpf']
            cpf_limpo = clean_cpf(cpf_raw)
            projeto = str(row['Projeto']).strip()
            nivel = str(row['Nível']).strip() if pd.notna(row['Nível']) else 'Outros'
            
            # 1. Buscar o Bolsista
            bolsista = None
            if cpf_limpo:
                bolsista = Bolsista.query.filter_by(cpf=cpf_limpo).first()
            
            if not bolsista:
                # Tenta buscar pelo nome exato (ou inicio)
                bolsista = Bolsista.query.filter(Bolsista.nome.ilike(f'{nome[:20]}%')).first()
                
            if not bolsista:
                not_found_count += 1
                print(f"[-] Bolsista NAO ENCONTRADO no banco: {nome} (CPF: {cpf_limpo})")
                continue
                
            # 2. Descobrir ou criar o Edital alvo
            edital_alvo = find_or_create_edital(projeto)
            
            if not edital_alvo:
                print(f"[-] Falha ao determinar Edital para o projeto: {projeto}")
                continue
                
            # Verifica se já está neste edital
            # Se não estiver, atualiza
            if bolsista.edital_id != edital_alvo.id:
                print(f"[>] Migrando {bolsista.nome} do Edital {bolsista.edital_id} -> Novo Edital {edital_alvo.id} ({edital_alvo.numero[:30]}...)")
                bolsista.edital_id = edital_alvo.id
                fixed_count += 1
                
            # 3. Garantir a Modalidade (Nível) no novo Edital
            mod = Modalidade.query.filter_by(edital_id=edital_alvo.id, nivel=nivel).first()
            if not mod:
                mod = Modalidade(
                    edital_id=edital_alvo.id,
                    nivel=nivel,
                    vagas=999,
                    valor_mensal=0.0
                )
                db.session.add(mod)
                db.session.flush()
            
            # 4. Atualizar o bolsista (se mudou de edital ou a modalidade não bate)
            if bolsista.modalidade_id != mod.id:
                bolsista.modalidade_id = mod.id
                
        # Commit todas as alterações
        try:
            db.session.commit()
            print(f"\n[OK] Migração concluida! {fixed_count} bolsistas realocados para Editais FA específicos.")
            print(f"     Bolsistas da planilha não encontrados no sistema: {not_found_count}")
        except Exception as e:
            db.session.rollback()
            print(f"\n[ERRO] Falha ao salvar no banco: {e}")

if __name__ == '__main__':
    print("Iniciando migração de Bolsistas FA...")
    run_migration()
