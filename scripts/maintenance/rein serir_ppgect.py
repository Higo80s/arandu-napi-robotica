"""
Verifica e reinsere programa PPGECT Ponta Grossa
"""

from app import app, db
from models import ProgramaAcademico, Campus

with app.app_context():
    # Buscar programa
    progs = ProgramaAcademico.query.filter(
        ProgramaAcademico.sigla_programa == 'PPGECT'
    ).all()
    
    resultado = []
    resultado.append("=== VERIFICANDO PPGECT ===\n")
    resultado.append(f"Programas encontrados: {len(progs)}\n")
    
    if progs:
        for p in progs:
            resultado.append(f"\nID: {p.id}")
            resultado.append(f"Nome: {p.nome_programa}")
            resultado.append(f"Sigla: {p.sigla_programa}")
            resultado.append(f"Campus: {p.campus.nome if p.campus else 'SEM CAMPUS'}")
            resultado.append(f"Campus ID: {p.campus_id}")
    else:
        resultado.append("\nPPGECT NAO ENCONTRADO! Verificando Campus PG...\n")
        
        # Buscar Campus PG
        pg = Campus.query.filter_by(sigla_campus='PG').first()
        if pg:
            resultado.append(f"Campus PG encontrado: ID={pg.id}, Nome={pg.nome}")
            
            # Inserir PPGECT
            resultado.append("\nInserindo PPGECT...")
            novo_prog = ProgramaAcademico(
                nome_programa="ENSINO DE CIENCIA E TECNOLOGIA",
                sigla_programa="PPGECT",
                codigo_programa="32001016088P0",
                campus_id=pg.id
            )
            db.session.add(novo_prog)
            db.session.commit()
            resultado.append(f"PPGECT inserido com sucesso! ID={novo_prog.id}")
        else:
            resultado.append("ERRO: Campus PG nao encontrado!")
    
    # Salvar resultado
    with open('resultado_ppgect.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(resultado))
    
    print('\n'.join(resultado))
