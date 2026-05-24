"""
Lista programas acadêmicos sem campus atribuído
Considera que campus pode ser NULL ou estar definido pela sigla
"""

from app import app
from models import ProgramaAcademico, Bolsista

with app.app_context():
    print("=== PROGRAMAS SEM CAMPUS ===\n")
    
    # Buscar programas sem campus_id
    programas_sem_campus = ProgramaAcademico.query.filter(
        (ProgramaAcademico.campus_id == None) | 
        (ProgramaAcademico.campus_id == 0)
    ).order_by(ProgramaAcademico.nome_programa).all()
    
    print(f"Total: {len(programas_sem_campus)} programas sem campus_id\n")
    
    if programas_sem_campus:
        print(f"{'ID':4s} | {'Código':18s} | {'Sigla':12s} | {'Nome':50s} | Bolsistas")
        print("-" * 100)
        
        for p in programas_sem_campus:
            # Contar bolsistas vinculados
            bolsistas_count = Bolsista.query.filter_by(
                programa_id=p.id,
                ativo=True
            ).count()
            
            codigo = p.codigo_programa or 'SEM CODIGO'
            sigla = p.sigla_programa or 'SEM SIGLA'
            nome = p.nome_programa[:50] if p.nome_programa else 'SEM NOME'
            
            print(f"{p.id:4d} | {codigo:18s} | {sigla:12s} | {nome:50s} | {bolsistas_count:3d}")
    else:
        print("OK - Todos os programas tem campus atribuido!")
    
    # Verificar se há programas com sigla de campus no nome
    print("\n=== PROGRAMAS QUE PODEM TER CAMPUS NA SIGLA ===\n")
    
    # Siglas comuns: CB, CT, CP, CM, DV, FB, GP, LD, MD, PB, PG, SH, TD, AP
    siglas_conhecidas = [
        'CB', 'CT', 'CP', 'CM', 'DV', 'FB', 'GP', 
        'LD', 'MD', 'PB', 'PG', 'SH', 'TD', 'AP'
    ]
    
    programas_com_sigla = []
    
    for p in programas_sem_campus:
        # Verificar se sigla do programa termina com sigla de campus
        if p.sigla_programa:
            for sigla_campus in siglas_conhecidas:
                if p.sigla_programa.endswith(f'-{sigla_campus}'):
                    programas_com_sigla.append((p, sigla_campus))
                    break
    
    if programas_com_sigla:
        print(f"Encontrados {len(programas_com_sigla)} programas com sigla de campus no nome:\n")
        
        for p, sigla in programas_com_sigla:
            bolsistas = Bolsista.query.filter_by(programa_id=p.id, ativo=True).count()
            print(f"  ID {p.id:3d}: {p.sigla_programa:15s} → Campus: {sigla} ({bolsistas} bolsistas)")
        
        print("\nSUGESTAO: Esses programas podem ser vinculados automaticamente aos campi!")
    else:
        print("Nenhum programa com sigla de campus identificada no nome.")
