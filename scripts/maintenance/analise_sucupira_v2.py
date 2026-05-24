import re
from datetime import datetime
from app import app, db
from models import Bolsista, ProgramaAcademico

def parse_line(line):
    # Pattern:
    # Discente PPG (Plataforma Sucupira) - CODIGO - NOME_PROG	Nivel	CPF - NOME	INICIO - FIM	SITUACAO
    # Tab separated usually, but looks like " - " separators too.
    # User input seems to be tab separated fields:
    # 1. "Discente PPG ... - COD - PROG"
    # 2. "Nivel" (Doutorado/Mestrado)
    # 3. "CPF - NOME"
    # 4. "INICIO - FIM"
    # 5. "Situacao"
    
    parts = line.split('\t')
    if len(parts) < 5:
        return None
        
    # Part 1: Program Info
    # Ex: "Discente PPG (Plataforma Sucupira) - 40006018008P6 - ENGENHARIA CIVIL"
    prog_info = parts[0]
    result_prog = re.search(r'(\d{10,}[A-Z\d]+)', prog_info)
    cod_programa = result_prog.group(1) if result_prog else "UNKNOWN"
    
    # Part 2: Level
    nivel = parts[1].strip()
    
    # Part 3: CPF - Name
    # Ex: "100.146.414-10 - ADELANIA DE OLIVEIRA SOUZA"
    cpf_name = parts[2]
    # CPF might need cleanup
    cpf_match = re.search(r'([\d\.-]+)\s-\s(.+)', cpf_name)
    if cpf_match:
        cpf_raw = cpf_match.group(1).replace('.', '').replace('-', '')
        nome = cpf_match.group(2).strip()
    else:
        cpf_raw = "UNKNOWN"
        nome = cpf_name
        
    # Part 4: Dates
    # Ex: "01/07/2023 - 30/06/2027"
    dates = parts[3]
    d_parts = dates.split(' - ')
    dt_inicio = datetime.strptime(d_parts[0].strip(), '%d/%m/%Y').date()
    dt_fim = datetime.strptime(d_parts[1].strip(), '%d/%m/%Y').date()
    
    return {
        'cod_programa': cod_programa,
        'nivel': nivel,
        'cpf': cpf_raw,
        'nome': nome,
        'inicio': dt_inicio,
        'fim': dt_fim
    }

def analyze():
    print("Iniciando Análise de Discrepâncias Sucupira vs DB...")
    
    # 1. Load File
    try:
        with open('sucupira_raw.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("Arquivo sucupira_raw.txt não encontrado.")
        return

    sucupira_data = []
    print(f"Lendo {len(lines)} registros do Sucupira...")
    
    for l in lines:
        if not l.strip(): continue
        parsed = parse_line(l.strip())
        if parsed:
            sucupira_data.append(parsed)
            
    print(f"Registros processados com sucesso: {len(sucupira_data)}")
    print("-" * 50)
    
    # 2. Compare with DB
    with app.app_context():
        # Get all active bolsistas
        db_bolsistas = Bolsista.query.filter_by(ativo=True).all()
        db_map = {b.cpf.replace('.', '').replace('-', ''): b for b in db_bolsistas if b.cpf}
        
        sucupira_only = []
        db_only = [] # We won't list all DB only, mainly those involved
        mismatches = []
        
        # Check Sucupira -> DB
        for s in sucupira_data:
            b_db = db_map.get(s['cpf'])
            
            if not b_db:
                sucupira_only.append(s)
            else:
                # Check for discrepancies
                issues = []
                # Check Level/Modality
                if b_db.modalidade and s['nivel'].upper() not in b_db.modalidade.nivel.upper():
                    issues.append(f"Nível Diferente: Sucupira={s['nivel']} vs DB={b_db.modalidade.nivel}")
                
                # Check End Date (tolerance of a few days?)
                if b_db.data_fim_bolsa != s['fim']:
                    issues.append(f"Fim Vigência: Sucupira={s['fim']} vs DB={b_db.data_fim_bolsa}")
                    
                if issues:
                    mismatches.append({'nome': s['nome'], 'cpf': s['cpf'], 'issues': issues})
                    
        # Report
        with open('relatorio_final.txt', 'w', encoding='utf-8') as f_out:
            f_out.write(f"Iniciando Análise de Discrepâncias Sucupira vs DB...\n")
            f_out.write(f"Registros processados: {len(sucupira_data)}\n")
            f_out.write("-" * 50 + "\n")
            
            f_out.write(f"\n[1] BOLSISTAS NO SUCUPIRA MAS NÃO NO SISTEMA (Total: {len(sucupira_only)})\n")
            f_out.write("(Estes alunos deveriam estar cadastrados?)\n")
            for x in sucupira_only:
                f_out.write(f" - {x['nome']} ({x['cpf']}) | Prog: {x['cod_programa']}\n")
                
            f_out.write(f"\n[2] DIVERGÊNCIAS DE DADOS (Total: {len(mismatches)})\n")
            for x in mismatches:
                f_out.write(f" - {x['nome']} ({x['cpf']}):\n")
                for i in x['issues']:
                    f_out.write(f"   * {i}\n")
            
            f_out.write("\nFim do Relatório.\n")
            
        print("Relatório gerado em relatorio_final.txt")

if __name__ == "__main__":
    analyze()
