import os
import sys
import csv
import datetime

# Setup paths to import 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Bolsista, ProgramaAcademico, Modalidade, Edital
from sqlalchemy import or_
from dateutil.relativedelta import relativedelta

FOMENTO_MAP = {
    'CAPES-DS': 'CAPES PPG',
    'CAPES-DS-GCUB': 'CAPES PPG',
    'Campus-RecursosPróprios': 'Recursos próprios campus',
    'UTFPR/Recursos Próprios2021': 'Recursos Próprios PROPPG',
    'UTFPR/Recursos Próprios2020': 'Recursos Próprios PROPPG',
    'CAPES-PROREITORIA': 'CAPES IES PROPPG',
    'PROFMAT': 'Bolsas PROFMAT',
    'Fundação Araucária': 'Fundação Araucária',
    'Bolsa Capes/FA': 'Fundação Araucária',
    'CNPq': 'CNPq',
    'DAI-CNPq': 'CNPq',
    'Fundação Araucária/NAPI': 'Fundação Araucária/NAPI',
    'PDSE': 'PDSE',
    'ANP': 'ANP',
    'Outra Fonte': 'Outra Fonte',
    'PROFEF': 'PROFEF'
}

def clean_cpf(cpf_str):
    return ''.join(filter(str.isdigit, str(cpf_str)))

def format_cpf(cpf_str):
    c = clean_cpf(cpf_str)
    if len(c) == 11:
        return f"{c[:3]}.{c[3:6]}.{c[6:9]}-{c[9:]}"
    return cpf_str

def parse_date(date_str):
    if not date_str or not date_str.strip() or date_str.strip() == '-' or len(date_str.strip()) < 10:
        return None
    try:
        return datetime.datetime.strptime(date_str.strip()[:10], '%d/%m/%Y').date()
    except ValueError:
        return None

CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'planilnhas_externas', 'Alunos_bolsistas_todos.csv')

def run_sync(filepath=CSV_PATH):
    print("Iniciando sincronização local a partir de:", filepath)
    if not os.path.exists(filepath):
        print("ARQUIVO_NÃO_ENCONTRADO:", filepath)
        return
        
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        return process_csv_stream(f)

def process_csv_stream(file_stream):
    """
    Processa um stream (ou arquivo aberto) do CSV UTFPR em memória.
    Retorna o dicionário de estatísticas ao invés de printar se for web.
    """
    with app.app_context():
        # Encontrar um edital fallback
        default_edital = Edital.query.order_by(Edital.id.desc()).first()
        stats = {'updated': 0, 'new': 0, 'closed': 0, 'errors': 0}
        
        reader = csv.reader(file_stream, delimiter=';')
        headers = []
        
        for row in reader:
            if not row: continue
            # The headers start with "Seq."
            if row[0].strip() == "Seq." or (len(row) > 1 and "Seq." in row[0]):
                headers = [str(h).replace('\n', ' ').strip() for h in row]
                break
        
        if not headers:
            print("ERRO: Não encontrou o cabeçalho 'Seq.'")
            return

        print("Cabeçalhos detectados:", headers)
        
        # Pre-cache or generate Editais mapping
        edital_cache = {}
        for fkey, fname in FOMENTO_MAP.items():
            if fname in edital_cache:
                continue
            
            if fname == 'CAPES PPG':
                ed = Edital.query.get(14)
            elif fname == 'Recursos Próprios PROPPG':
                ed = Edital.query.get(1)
            elif fname == 'CAPES IES PROPPG':
                ed = Edital.query.get(13)
            else:
                ed = Edital.query.filter_by(agencia=fname).first()
                if not ed:
                    ed = Edital(numero="GERAL", agencia=fname, descricao=f"Edital Geral - {fname}")
                    db.session.add(ed)
                    db.session.flush() # Pega o ID do edital para criar a modalidade a seguir
                    
                    # [FIX] Criar Modalidades base para novos editais automaticamente para o bolsista não ficar órfão
                    mod_mestrado = Modalidade(edital_id=ed.id, nivel="Mestrado", vagas=999, valor_mensal=0.0)
                    mod_doutorado = Modalidade(edital_id=ed.id, nivel="Doutorado", vagas=999, valor_mensal=0.0)
                    mod_mp = Modalidade(edital_id=ed.id, nivel="Mestrado Profissional", vagas=999, valor_mensal=0.0)
                    db.session.add_all([mod_mestrado, mod_doutorado, mod_mp])
                    
                    db.session.commit()
            
            if ed:
                edital_cache[fname] = ed.id
        
        # Carregar bolsistas em memória para bypass da criptografia SQLAlchemy no filter_by
        todos_bolsistas = Bolsista.query.all()
        bolsistas_dict_ativos = {}
        bolsistas_dict_inativos = {}
        for b in todos_bolsistas:
            if not b.cpf: continue
            # Priorizar o mais recente ativo
            if b.ativo:
                bolsistas_dict_ativos[b.cpf] = b
            else:
                bolsistas_dict_inativos[b.cpf] = b

        for raw_row in reader:
            row = [str(cell).replace('"', '').strip() for cell in raw_row]
            if len(row) < 18: continue
            
            try:
                c_campus = row[1].strip()  # Campus
                c_programa = row[2].strip() # Programa
                c_codigo = row[3].strip() or None  # Código/RA
                c_nivel = row[5].strip()   # MA/DT/MP
                c_nome = row[6].strip()
                c_data_ingresso = row[7].strip()
                c_defesa = row[9].strip()  # Data Defesa
                c_cpf = format_cpf(row[11])
                c_sexo = row[13].strip()
                c_fonte = row[14].strip()
                c_data_inicio = row[15].strip()
                c_data_fim = row[16].strip()
                c_email = row[18].strip() if len(row) > 18 else ''
            except IndexError as e:
                print(f"IndexError on row: {row}")
                stats['errors'] += 1
                continue

            if not c_cpf:
                continue
            
            dt_defesa = parse_date(c_defesa)
            dt_inicio = parse_date(c_data_inicio)
            dt_fim = parse_date(c_data_fim)
            
            fomento_name = FOMENTO_MAP.get(c_fonte, c_fonte)
            correct_edital_id = edital_cache.get(fomento_name) or default_edital.id
            
            # Retrieve from db via dictionary
            bolsista = bolsistas_dict_ativos.get(c_cpf) or bolsistas_dict_inativos.get(c_cpf)
            
            if bolsista:
                # Update RA and email
                if c_codigo:
                    bolsista.registro_academico = c_codigo
                if c_email and not bolsista.email:
                    bolsista.email = c_email
                
                # Relocate if currently in the generic fallback Edital OR if we need to sync to correct_edital_id
                if bolsista.edital_id != correct_edital_id and correct_edital_id:
                    bolsista.edital_id = correct_edital_id
                    
                    # [FIX] Ao trocar de edital, precisamos fixar a modalidade pro novo edital
                    target_nivel = "Mestrado"
                    if bolsista.modalidade_id:
                        old_mod = Modalidade.query.get(bolsista.modalidade_id)
                        if old_mod:
                            target_nivel = old_mod.nivel
                            
                    new_mod = Modalidade.query.filter_by(edital_id=correct_edital_id, nivel=target_nivel).first()
                    if not new_mod:
                        new_mod = Modalidade(edital_id=correct_edital_id, nivel=target_nivel, vagas=999, valor_mensal=0.0)
                        db.session.add(new_mod)
                        db.session.flush()
                    bolsista.modalidade_id = new_mod.id
                
                # Try to map Program if missing
                if not bolsista.programa_id and c_programa:
                    prog = ProgramaAcademico.query.filter(or_(ProgramaAcademico.sigla_programa == c_programa, ProgramaAcademico.nome_programa.ilike(f"%{c_programa}%"))).first()
                    if prog:
                        bolsista.programa_id = prog.id
                
                # Update legacy fields
                bolsista.campus = c_campus
                bolsista.programa = c_programa
                
                # Trava de Defesa Antecipada - Revenue Save
                if dt_defesa and bolsista.ativo:
                    bolsista.ativo = False
                    bolsista.data_fim_bolsa = dt_defesa
                    bolsista.motivo_desligamento = f"Defesa Antecipada em {dt_defesa.strftime('%d/%m/%Y')} (Sinc. CSV UTFPR)"
                    stats['closed'] += 1
                    print(f"[DEFESA] {bolsista.nome} - Bolsa encerrada: Defendeu em {dt_defesa}")
                
                stats['updated'] += 1
            else:
                # Precisaria achar o Programa e a modalidade.
                mapping_nivel = {'MA': 'Mestrado', 'DT': 'Doutorado', 'MP': 'Mestrado Profissional'}
                nivel_str = mapping_nivel.get(c_nivel, 'Mestrado')
                
                # Fetch a valid mod from the targeted Edital! Not just any mod.
                mod = Modalidade.query.filter_by(edital_id=correct_edital_id, nivel=nivel_str).first()
                # Create ad-hoc if missing
                if not mod and correct_edital_id:
                    mod = Modalidade(edital_id=correct_edital_id, nivel=nivel_str, vagas=999, valor_mensal=0.0)
                    db.session.add(mod)
                    db.session.flush()
                
                if mod and correct_edital_id and dt_inicio and dt_fim:
                    # Calcular meses_duracao approximado
                    rd = relativedelta(dt_fim, dt_inicio)
                    meses = rd.years * 12 + rd.months
                    if rd.days > 15: meses += 1
                    if meses <= 0: meses = 24
                    
                    prog = ProgramaAcademico.query.filter(or_(ProgramaAcademico.sigla_programa == c_programa, ProgramaAcademico.nome_programa.ilike(f"%{c_programa}%"))).first()
                    prog_id = prog.id if prog else None
                    
                    novo_bolsista = Bolsista(
                        edital_id=correct_edital_id,
                        modalidade_id=mod.id,
                        programa_id=prog_id,
                        campus=c_campus,
                        programa=c_programa,
                        nome=c_nome,
                        cpf=c_cpf,
                        email=c_email,
                        registro_academico=c_codigo,
                        data_inicio_bolsa=dt_inicio,
                        data_fim_bolsa=dt_fim,
                        meses_duracao=meses,
                        ativo=not bool(dt_defesa)
                    )
                    
                    if dt_defesa:
                        novo_bolsista.data_fim_bolsa = dt_defesa
                        novo_bolsista.motivo_desligamento = f"Defesa Antecipada prévia em {dt_defesa.strftime('%d/%m/%Y')} (Carga inicial)"
                        stats['closed'] += 1
                        
                    db.session.add(novo_bolsista)
                    stats['new'] += 1
                else:
                    print(f"FAILED to create new bolsista {c_nome}: mod={mod}, edital={default_edital}, dt_inicio={dt_inicio}, dt_fim={dt_fim}, cpf={c_cpf}")
                    stats['errors'] += 1
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Erro ao salvar/atualizar o CPF {c_cpf}: {e}")
                stats['errors'] += 1
                
    print(f"\n====================================")
    print(f"Sincronização Finalizada com Sucesso!")
    print(f"Atualizados (existentes): {stats['updated']}")
    print(f"Novos cadastrados: {stats['new']}")
    print(f"Bolsas Encerradas (trava defesa): {stats['closed']}")
    print(f"Erros de parse row: {stats['errors']}")
    print(f"====================================")
    
    return stats

if __name__ == '__main__':
    run_sync()
