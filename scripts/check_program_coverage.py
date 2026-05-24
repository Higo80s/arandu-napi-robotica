"""
Verificar se todos os programas de /admin/programas aparecem em /reports/evolution/view
Comparando pelo código do programa
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import ProgramaAcademico, BolsaVolumetriaAnual

print("="*80)
print("VERIFICANDO COBERTURA DE PROGRAMAS NO RELATÓRIO DE EVOLUÇÃO")
print("="*80)
print()

with app.app_context():
    # 1. Todos os programas cadastrados no sistema
    todos_programas = ProgramaAcademico.query.all()
    codigos_todos = set([p.codigo_programa for p in todos_programas])
    
    print(f"Total de programas cadastrados: {len(codigos_todos)}")
    
    # 2. Programas que têm dados de volumetria (aparecem no relatório)
    programas_com_bolsas = db.session.query(
        BolsaVolumetriaAnual.programa_id
    ).distinct().all()
    
    programas_ids_com_bolsas = set([p[0] for p in programas_com_bolsas])
    
    # Pegar códigos
    codigos_com_bolsas = set()
    for prog in todos_programas:
        if prog.id in programas_ids_com_bolsas:
            codigos_com_bolsas.add(prog.codigo_programa)
    
    print(f"Programas com dados no relatório: {len(codigos_com_bolsas)}")
    
    # 3. Programas SEM dados
    codigos_sem_bolsas = codigos_todos - codigos_com_bolsas
    
    print()
    print("="*80)
    print("RESULTADO")
    print("="*80)
    
    if codigos_sem_bolsas:
        print(f"\n⚠️  {len(codigos_sem_bolsas)} PROGRAMAS SEM DADOS NO RELATÓRIO:")
        print()
        
        for codigo in sorted(codigos_sem_bolsas):
            prog = next((p for p in todos_programas if p.codigo_programa == codigo), None)
            if prog:
                print(f"  - {codigo}: {prog.nome_programa} ({prog.sigla_programa}) - Campus {prog.campus.sigla_campus}")
    else:
        print("\n✅ TODOS os programas cadastrados TÊM dados no relatório!")
    
    print()
    print("="*80)
    print("RESUMO")
    print("="*80)
    print(f"Total cadastrados: {len(codigos_todos)}")
    print(f"Com dados: {len(codigos_com_bolsas)}")
    print(f"Sem dados: {len(codigos_sem_bolsas)}")
    print(f"Cobertura: {len(codigos_com_bolsas)/len(codigos_todos)*100:.1f}%")
