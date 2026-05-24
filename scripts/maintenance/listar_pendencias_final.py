"""
Gerar lista final de pendencias apos correcoes
Compara banco atualizado com Sucupira
"""

from app import app
from models import ProgramaAcademico
from auditar_programas_sucupira import SUCUPIRA_DATA

with app.app_context():
    # Buscar programas do banco
    programas_db = ProgramaAcademico.query.all()
    db_dict = {p.codigo_programa: p for p in programas_db if p.codigo_programa}
    sucupira_dict = {s['codigo']: s for s in SUCUPIRA_DATA}
    
    # Categorizar pendências
    pendencias = {
        'excedentes_grad': [],  # Graduação
        'excedentes_posgrad': [],  # Pós-graduação que não está na Sucupira
        'divergencias': [],  # Diferenças de dados
        'multicampi': [],  # Programas multicampi
    }
    
    # Analisar excedentes
    for codigo, prog in db_dict.items():
        if codigo not in sucupira_dict:
            # Verificar se é graduação
            if prog.niveis == 'GRAD' or 'GRAD-' in codigo:
                pendencias['excedentes_grad'].append({
                    'codigo': codigo,
                    'nome': prog.nome_programa,
                    'sigla': prog.sigla_programa,
                    'campus': prog.campus.sigla_campus if prog.campus else 'N/I'
                })
            else:
                pendencias['excedentes_posgrad'].append({
                    'codigo': codigo,
                    'nome': prog.nome_programa,
                    'sigla': prog.sigla_programa,
                    'campus': prog.campus.sigla_campus if prog.campus else 'N/I',
                    'niveis': prog.niveis or 'N/I'
                })
    
    # Analisar divergências
    for codigo in set(db_dict.keys()) & set(sucupira_dict.keys()):
        prog = db_dict[codigo]
        suc = sucupira_dict[codigo]
        
        diffs = []
        
        # Comparar dados
        if prog.nome_programa.upper().replace('Ê', 'E').replace('Ã', 'A').strip() != suc['nome'].upper().replace('Ê', 'E').replace('Ã', 'A').strip():
            diffs.append(f"Nome: BD='{prog.nome_programa}' vs Sucupira='{suc['nome']}'")
        
        campus_db = prog.campus.sigla_campus if prog.campus else "N/I"
        
        # Detectar multicampi
        if '/' in suc['campus']:
            pendencias['multicampi'].append({
                'codigo': codigo,
                'nome': prog.nome_programa,
                'sigla': prog.sigla_programa,
                'campus_bd': campus_db,
                'campus_sucupira': suc['campus'],
                'nota': 'Programa funciona em multiplos campi'
            })
        elif campus_db != suc['campus']:
            diffs.append(f"Campus: BD='{campus_db}' vs Sucupira='{suc['campus']}'")
        
        prog_niveis = prog.niveis or "N/I"
        if prog_niveis != suc['niveis']:
            diffs.append(f"Niveis: BD='{prog_niveis}' vs Sucupira='{suc['niveis']}'")
        
        if diffs:
            pendencias['divergencias'].append({
                'codigo': codigo,
                'programa': prog.sigla_programa,
                'diferencas': diffs
            })
    
    # IMPRIMIR RELATÓRIO
    print("\n" + "=" * 80)
    print("LISTA FINAL DE PENDENCIAS")
    print("=" * 80)
    
    # 1. Cursos de Graduação
    if pendencias['excedentes_grad']:
        print(f"\n1. CURSOS DE GRADUACAO ({len(pendencias['excedentes_grad'])})")
        print("-" * 80)
        print("ACAO: Manter no banco (nao estao na Sucupira por serem graduacao)")
        for idx, prog in enumerate(pendencias['excedentes_grad'], 1):
            print(f"{idx}. {prog['codigo']} - {prog['nome']}")
            print(f"   Sigla: {prog['sigla']} | Campus: {prog['campus']}")
    
    # 2. Pós-graduação excedentes
    if pendencias['excedentes_posgrad']:
        print(f"\n2. POS-GRADUACAO NAO ENCONTRADA NA SUCUPIRA ({len(pendencias['excedentes_posgrad'])})")
        print("-" * 80)
        print("ACAO SUGERIDA: Revisar se sao programas descontinuados ou duplicatas")
        for idx, prog in enumerate(pendencias['excedentes_posgrad'], 1):
            print(f"{idx}. {prog['codigo']} - {prog['nome']}")
            print(f"   Sigla: {prog['sigla']} | Campus: {prog['campus']} | Niveis: {prog['niveis']}")
    
    # 3. Divergências
    if pendencias['divergencias']:
        print(f"\n3. DIVERGENCIAS DE DADOS ({len(pendencias['divergencias'])})")
        print("-" * 80)
        print("ACAO SUGERIDA: Corrigir conforme Plataforma Sucupira")
        for idx, div in enumerate(pendencias['divergencias'], 1):
            print(f"{idx}. {div['codigo']} - {div['programa']}")
            for diff in div['diferencas']:
                print(f"   - {diff}")
    
    # 4. Multicampi
    if pendencias['multicampi']:
        print(f"\n4. PROGRAMAS MULTICAMPI ({len(pendencias['multicampi'])})")
        print("-" * 80)
        print("ACAO: Aceitar diferenca - bolsistas devem ser cadastrados no campus especifico")
        for idx, prog in enumerate(pendencias['multicampi'], 1):
            print(f"{idx}. {prog['codigo']} - {prog['sigla']}")
            print(f"   Campus BD: {prog['campus_bd']} | Sucupira: {prog['campus_sucupira']}")
            print(f"   {prog['nota']}")
    
    # Resumo
    print("\n" + "=" * 80)
    print("RESUMO")
    print("=" * 80)
    print(f"Graduacao (manter): {len(pendencias['excedentes_grad'])}")
    print(f"Pos-grad excedentes (revisar): {len(pendencias['excedentes_posgrad'])}")
    print(f"Divergencias (corrigir): {len(pendencias['divergencias'])}")
    print(f"Multicampi (aceitar): {len(pendencias['multicampi'])}")
    print("=" * 80)
