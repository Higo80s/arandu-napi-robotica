"""
Gerar lista em formato JSON para exibição no chat
"""

from app import app
from models import ProgramaAcademico, Bolsista
from auditar_programas_sucupira import SUCUPIRA_DATA
import json

with app.app_context():
    programas_db = ProgramaAcademico.query.all()
    db_dict = {p.codigo_programa: p for p in programas_db if p.codigo_programa}
    sucupira_dict = {s['codigo']: s for s in SUCUPIRA_DATA}
    
    excedentes_pos = []
    
    for codigo, prog in db_dict.items():
        if codigo not in sucupira_dict:
            if prog.niveis != 'GRAD' and 'GRAD-' not in codigo:
                bolsistas_count = Bolsista.query.filter_by(programa_id=prog.id).count()
                
                excedentes_pos.append({
                    'codigo': codigo,
                    'nome': prog.nome_programa,
                    'sigla': prog.sigla_programa,
                    'campus': prog.campus.sigla_campus if prog.campus else 'N/I',
                    'niveis': prog.niveis or 'N/I',
                    'nota': str(prog.nota_capes) if prog.nota_capes else 'N/I',
                    'bolsistas': bolsistas_count
                })
    
    # Ordenar por número de bolsistas (decrescente) e depois por nome
    excedentes_pos.sort(key=lambda x: (-x['bolsistas'], x['nome']))
    
    # Imprimir formatado
    print("\n" + "=" * 100)
    print(f"LISTA COMPLETA: {len(excedentes_pos)} PROGRAMAS DE POS-GRADUACAO EXCEDENTES")
    print("=" * 100)
    print("\nPrograma | Sigla | Campus | Niveis | Bolsistas | Sugestao")
    print("-" * 100)
    
    for idx, p in enumerate(excedentes_pos, 1):
        # Sugestão
        if p['bolsistas'] == 0:
            sug = "EXCLUIR (sem bolsistas)"
        elif 'PPGEM' in p['sigla'] or 'PPGEA' in p['sigla'] or 'PPGEN' in p['sigla']:
            sug = "Verificar duplicata multicampi"
        else:
            sug = "Verificar se descontinuado"
        
        print(f"{idx:2d}. {p['codigo']:15s} | {p['sigla']:10s} | {p['campus']:6s} | {p['niveis']:6s} | {p['bolsistas']:3d} | {sug}")
    
    print("\n" + "=" * 100)
    print("RESUMO PARA DECISAO")
    print("=" * 100)
    
    com_bolsistas = [p for p in excedentes_pos if p['bolsistas'] > 0]
    sem_bolsistas = [p for p in excedentes_pos if p['bolsistas'] == 0]
    
    print(f"\nCOM bolsistas vinculados: {len(com_bolsistas)} programas (MANTER ou revisar se multicampi)")
    print(f"SEM bolsistas vinculados: {len(sem_bolsistas)} programas (candidatos a EXCLUSAO)")
    
    if sem_bolsistas:
        print(f"\nCandidatos a exclusao:")
        for p in sem_bolsistas:
            print(f"  - {p['codigo']} ({p['sigla']})")
    
    print("=" * 100)
