"""
Auditoria completa de programas acadêmicos
Identifica programas com problemas de níveis
"""

from app import app, db
from models import ProgramaAcademico, Bolsista, Campus
from collections import defaultdict

with app.app_context():
    print("=== AUDITORIA DE PROGRAMAS ACADEMICOS ===\n")
    
    # Buscar todos os programas
    programas = ProgramaAcademico.query.order_by(ProgramaAcademico.campus_id, ProgramaAcademico.nome_programa).all()
    
    # Categorizar problemas
    sem_niveis = []
    com_niveis = []
    niveis_unicos = set()
    
    for p in programas:
        bolsistas_count = Bolsista.query.filter_by(programa_id=p.id).count()
        campus_nome = p.campus.nome if p.campus else "SEM CAMPUS"
        
        programa_info = {
            'id': p.id,
            'nome': p.nome_programa,
            'sigla': p.sigla_programa,
            'codigo': p.codigo_programa,
            'campus': campus_nome,
            'campus_id': p.campus_id,
            'niveis': p.niveis,
            'bolsistas': bolsistas_count
        }
        
        if p.niveis is None or p.niveis == '' or p.niveis == 'None':
            sem_niveis.append(programa_info)
        else:
            com_niveis.append(programa_info)
            # Extrair níveis únicos
            for nivel in p.niveis.split(','):
                niveis_unicos.add(nivel.strip())
    
    # Relatório
    print(f"TOTAL DE PROGRAMAS: {len(programas)}")
    print(f"  - Com níveis definidos: {len(com_niveis)}")
    print(f"  - SEM níveis (PROBLEMA!): {len(sem_niveis)}")
    print(f"\nNíveis únicos encontrados: {sorted(niveis_unicos)}\n")
    
    # Programas SEM níveis
    print("=" * 100)
    print("PROGRAMAS SEM NÍVEIS (PRECISAM CORREÇÃO)")
    print("=" * 100)
    
    if sem_niveis:
        # Agrupar por campus
        por_campus = defaultdict(list)
        for p in sem_niveis:
            por_campus[p['campus']].append(p)
        
        for campus in sorted(por_campus.keys()):
            print(f"\n📍 {campus}:")
            print("-" * 100)
            for p in por_campus[campus]:
                print(f"  ID {p['id']:3d} | {p['codigo']:15s} | {p['sigla']:12s} | {p['nome']:50s} | {p['bolsistas']:3d} bolsistas")
    else:
        print("✅ Nenhum programa sem níveis!")
    
    # Salvar relatório em arquivo
    with open('auditoria_programas.txt', 'w', encoding='utf-8') as f:
        f.write("AUDITORIA DE PROGRAMAS ACADEMICOS\n")
        f.write("=" * 100 + "\n\n")
        
        f.write(f"TOTAL: {len(programas)} programas\n")
        f.write(f"  - Com níveis: {len(com_niveis)}\n")
        f.write(f"  - SEM níveis: {len(sem_niveis)}\n\n")
        
        f.write("PROGRAMAS SEM NIVEIS:\n")
        f.write("-" * 100 + "\n")
        
        for campus in sorted(por_campus.keys()):
            f.write(f"\n{campus}:\n")
            for p in por_campus[campus]:
                f.write(f"  ID {p['id']}, {p['codigo']}, {p['sigla']}, {p['nome']}, {p['bolsistas']} bolsistas\n")
    
    print(f"\n\n✅ Relatório salvo em: auditoria_programas.txt")
    
    # Estatísticas de bolsistas afetados
    total_bolsistas_afetados = sum(p['bolsistas'] for p in sem_niveis)
    print(f"\n⚠️  IMPACTO: {total_bolsistas_afetados} bolsistas vinculados a programas SEM níveis definidos!")
