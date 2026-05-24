"""
Verifica bolsistas sem campus no relatório
Lista nome e CPF para validação
"""

from app import app
from models import Bolsista

with app.app_context():
    print("=== BOLSISTAS SEM CAMPUS (NÃO INFORMADO) ===\n")
    
    # Buscar ativos sem campus
    bolsistas_sem_campus = Bolsista.query.filter(
        Bolsista.ativo == True
    ).filter(
        (Bolsista.campus == None) | 
        (Bolsista.campus == '') |
        (Bolsista.campus == 'N/I') |
        (Bolsista.campus.ilike('%não informado%'))
    ).order_by(Bolsista.nome).all()
    
    # Separar por nível
    mestrado = []
    doutorado = []
    outros = []
    
    for b in bolsistas_sem_campus:
        if b.modalidade:
            nivel = b.modalidade.nivel.upper()
            if 'MESTRADO' in nivel or 'MASTER' in nivel:
                mestrado.append(b)
            elif 'DOUTORADO' in nivel or 'DOCTOR' in nivel or 'PHD' in nivel:
                doutorado.append(b)
            else:
                outros.append(b)
        else:
            outros.append(b)
    
    print(f"Total: {len(bolsistas_sem_campus)} bolsistas\n")
    print(f"Mestrado: {len(mestrado)}")
    print(f"Doutorado: {len(doutorado)}")
    if outros:
        print(f"Outros: {len(outros)}")
    print()
    
    # MESTRADO
    if mestrado:
        print("=" * 80)
        print("MESTRADO ({} bolsistas)".format(len(mestrado)))
        print("=" * 80)
        for idx, b in enumerate(mestrado, 1):
            programa = b.programa or (b.programa_link.nome_programa if b.programa_link else 'SEM PROGRAMA')
            print(f"{idx:2d}. {b.nome:50s} | CPF: {b.cpf:15s} | {programa}")
        print()
    
    # DOUTORADO
    if doutorado:
        print("=" * 80)
        print("DOUTORADO ({} bolsistas)".format(len(doutorado)))
        print("=" * 80)
        for idx, b in enumerate(doutorado, 1):
            programa = b.programa or (b.programa_link.nome_programa if b.programa_link else 'SEM PROGRAMA')
            print(f"{idx:2d}. {b.nome:50s} | CPF: {b.cpf:15s} | {programa}")
        print()
    
    # RESUMO
    print("=" * 80)
    print("RESUMO COMPARATIVO")
    print("=" * 80)
    print(f"Sistema encontrou:  {len(mestrado)}M + {len(doutorado)}D = {len(bolsistas_sem_campus)} total")
    print(f"Relatório mostra:   28M + 18D = 46 total")
    print()
    
    if len(mestrado) == 28 and len(doutorado) == 18:
        print("✅ NÚMEROS CONFEREM COM O RELATÓRIO!")
    else:
        diff_m = len(mestrado) - 28
        diff_d = len(doutorado) - 18
        print(f"⚠️  DIVERGÊNCIA:")
        print(f"    Mestrado:  {diff_m:+d}")
        print(f"    Doutorado: {diff_d:+d}")
