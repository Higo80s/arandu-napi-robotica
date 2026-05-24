"""
Script simplificado - sem caracteres especiais
"""
from app import app
from models import ProgramaAcademico, Bolsista
from auditar_programas_sucupira import SUCUPIRA_DATA

with app.app_context():
    programas_db = ProgramaAcademico.query.all()
    db_dict = {p.codigo_programa: p for p in programas_db if p.codigo_programa}
    sucupira_dict = {s['codigo']: s for s in SUCUPIRA_DATA}
    
    excedentes_pos = []
    
    for codigo, prog in db_dict.items():
        if codigo not in sucupira_dict:
            if prog.niveis != 'GRAD' and 'GRAD-' not in codigo:
                bolsistas_count = Bolsista.query.filter_by(programa_id=prog.id).count()
                
                excedentes_pos.append([
                    codigo,
                    prog.sigla_programa,
                    prog.campus.sigla_campus if prog.campus else 'N/I',
                    prog.niveis or 'N/I',
                    bolsistas_count,
                    prog.nome_programa
                ])
    
    # Ordenar
    excedentes_pos.sort(key=lambda x: (-x[4], x[5]))
    
    # Salvar CSV simples
    with open('excedentes.csv', 'w', encoding='utf-8') as f:
        f.write("Num,Codigo,Sigla,Campus,Niveis,Bolsistas,Nome,Sugestao\n")
        
        for idx, p in enumerate(excedentes_pos, 1):
            if p[4] == 0:
                sug = "EXCLUIR"
            elif 'PPGEM' in p[1] or 'PPGEA' in p[1]:
                sug = "VER_DUPLICATA"
            else:
                sug = "REVISAR"
            
            f.write(f'{idx},{p[0]},{p[1]},{p[2]},{p[3]},{p[4]},"{p[5]}",{sug}\n')
    
    print(f"Total: {len(excedentes_pos)} programas")
    print(f"Com bolsistas: {sum(1 for p in excedentes_pos if p[4] > 0)}")
    print(f"Sem bolsistas: {sum(1 for p in excedentes_pos if p[4] == 0)}")
