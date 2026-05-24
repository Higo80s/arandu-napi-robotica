"""
Corrigir códigos incorretos e calcular total final de programas
"""

from app import app, db
from models import ProgramaAcademico

# Mapeamento de códigos errados -> corretos
CORRECOES_CODIGOS = {
    '40001016175D2': '40001016175P8',  # PPGAB Doutorado
    '40002012171M8': '40002012171P9',  # PPGAEE Mestrado (era o doutorado antes)
    '40006018024M1': '40006018024P1',  # PPGEM CP/PG
    '40006018027D8': '40006018027P0',  # PPGEN (era código do doutorado)
    '40006018174M3': '40006018174P3',  # PPGEA FB
    '40006018023M5': '40006018023P5',  # PPGEA LD/AP
    '40006018041M3': '40006018041P3',  # PPGMAT LD/CP
    '40006018015M2': '40006018015P2',  # PPGTAL LD/FB
    '40006018034M7': '40006018034P7',  # PPGTCA MD
}

# Programas para EXCLUIR (24 sem bolsistas)
EXCLUIR = [
    '40002012171D0', '40006018015D2', '40006018023D5', '40006018024D1', 
    '40006018027D4', '40006018029P3', '40006018034D7', '40006018037M6', 
    '40006018037D6', '40006018041M9', '40006018170M8', '40006018174D3', 
    '40006018175M0', '40006018175D0', '40006018182M6', '40006018183M2', 
    '40006018184P9', '40006018185P5', '40065013009M8', '40065013009D9', 
    '40065013010M0', '40065013010D1', '40065013018M1', '40065013018D2'
]

with app.app_context():
    print("=" * 80)
    print("CORRECOES FINAIS E EXCLUSOES")
    print("=" * 80)
    
    # 1. Corrigir códigos
    print("\n1. CORRIGINDO CODIGOS ERRADOS")
    print("-" * 80)
    
    for errado, correto in CORRECOES_CODIGOS.items():
        prog_errado = ProgramaAcademico.query.filter_by(codigo_programa=errado).first()
        prog_correto = ProgramaAcademico.query.filter_by(codigo_programa=correto).first()
        
        if prog_errado and prog_correto:
            print(f"  [{errado}] -> JA EXISTE correto [{correto}]")
            print(f"    Transferindo {prog_errado.bolsistas.count()} bolsistas...")
            
            # Transferir bolsistas para o programa correto
            for bolsista in prog_errado.bolsistas:
                bolsista.programa_id = prog_correto.id
            
            # Excluir programa errado
            db.session.delete(prog_errado)
            print(f"    Programa errado EXCLUIDO")
        elif prog_errado:
            print(f"  [{errado}] -> Corrigindo para [{correto}]")
            prog_errado.codigo_programa = correto
        else:
            print(f"  [{errado}] NAO ENCONTRADO")
    
    db.session.commit()
    
    # 2. Excluir programas sem bolsistas
    print("\n2. EXCLUINDO 24 PROGRAMAS SEM BOLSISTAS")
    print("-" * 80)
    
    excluidos = 0
    for codigo in EXCLUIR:
        prog = ProgramaAcademico.query.filter_by(codigo_programa=codigo).first()
        if prog:
            print(f"  [{codigo}] {prog.sigla_programa} EXCLUIDO")
            db.session.delete(prog)
            excluidos += 1
        else:
            print(f"  [{codigo}] NAO ENCONTRADO (ja pode ter sido excluido)")
    
    db.session.commit()
    print(f"\n  Total excluido: {excluidos}")
    
    # 3. Calcular totais FINAIS
    print("\n" + "=" * 80)
    print("TOTAL FINAL DE PROGRAMAS DE POS-GRADUACAO UTFPR")
    print("=" * 80)
    
    todos_programas = ProgramaAcademico.query.filter(
        ProgramaAcademico.niveis != 'GRAD',
        ~ProgramaAcademico.codigo_programa.like('GRAD-%')
    ).all()
    
    # Contar por nível
    mestrado_academico = 0
    mestrado_profissional = 0
    doutorado_academico = 0
    doutorado_profissional = 0
    mestrado_doutorado = 0  # Programas com M,D
    
    for prog in todos_programas:
        niveis = prog.niveis or ""
        
        if 'M,D' in niveis or ('M' in niveis and 'D' in niveis and ',' in niveis):
            mestrado_doutorado += 1
        elif 'MP,DP' in niveis:
            mestrado_profissional += 1
            doutorado_profissional += 1
        elif 'MP,D' in niveis:
            mestrado_profissional += 1
            doutorado_academico += 1
        elif niveis == 'M':
            mestrado_academico += 1
        elif niveis == 'MP':
            mestrado_profissional += 1
        elif niveis == 'D':
            doutorado_academico += 1
        elif niveis == 'DP':
            doutorado_profissional += 1
    
    # Total de mestrados
    total_mestrados = mestrado_academico + mestrado_profissional + mestrado_doutorado
    
    # Total de doutorados
    total_doutorados = doutorado_academico + doutorado_profissional + mestrado_doutorado
    
    print(f"\nMESTRADOS:")
    print(f"  Academico: {mestrado_academico}")
    print(f"  Profissional: {mestrado_profissional}")
    print(f"  Programas M+D: {mestrado_doutorado}")
    print(f"  TOTAL MESTRADOS: {total_mestrados}")
    
    print(f"\nDOUTORADOS:")
    print(f"  Academico: {doutorado_academico}")
    print(f"  Profissional: {doutorado_profissional}")
    print(f"  Programas M+D: {mestrado_doutorado}")
    print(f"  TOTAL DOUTORADOS: {total_doutorados}")
    
    print(f"\nTOTAL PROGRAMAS POS-GRADUACAO: {len(todos_programas)}")
    print(f"(Programas que ofertam M+D contam para ambos os totais)")
    
    print("\n" + "=" * 80)
    print("VALIDACAO COM SUCUPIRA")
    print("=" * 80)
    
    from auditar_programas_sucupira import SUCUPIRA_DATA
    
    # Contar na Sucupira
    sucupira_m = sum(1 for s in SUCUPIRA_DATA if 'M' in s['niveis'])
    sucupira_d = sum(1 for s in SUCUPIRA_DATA if 'D' in s['niveis'])
    
    print(f"Sucupira: {sucupira_m} mestrados, {sucupira_d} doutorados")
    print(f"Banco (apos correcoes): {total_mestrados} mestrados, {total_doutorados} doutorados")
    
    if total_mestrados == sucupira_m and total_doutorados == sucupira_d:
        print("\n>>> PERFEITO! Banco e Sucupira ALINHADOS!")
    else:
        print(f"\n>>> Diferença: M={total_mestrados-sucupira_m}, D={total_doutorados-sucupira_d}")
    
    print("=" * 80)
