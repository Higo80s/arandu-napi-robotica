"""
Replica EXATA lógica do relatório campus consolidado
para identificar os "NÃO INFORMADO"
"""

from app import app
from models import Bolsista

with app.app_context():
    print("=== REPLICANDO LÓGICA DO RELATÓRIO ===\n")
    
    # Buscar TODOS bolsistas (como o relatório faz)
    bolsistas = Bolsista.query.all()
    
    print(f"Total de bolsistas no sistema: {len(bolsistas)}\n")
    
    # Separar os "NÃO INFORMADO" usando MESMA lógica do relatório
    sem_campus_mestrado = []
    sem_campus_doutorado = []
    
    for b in bolsistas:
        # MESMA LÓGICA DO RELATÓRIO (linhas 21-27)
        if b.programa_link and b.programa_link.campus:
            # Tem programa_link E campus - OK
            continue
        elif b.programa and '(' in b.programa:
            # Tem campus no texto - OK
            continue
        else:
            # NÃO INFORMADO!
            if not b.modalidade:
                continue
            
            nivel = b.modalidade.nivel.upper()
            if 'MESTRADO' in nivel or 'MASTER' in nivel:
                sem_campus_mestrado.append(b)
            elif 'DOUTORADO' in nivel or 'DOCTOR' in nivel or 'PHD' in nivel:
                sem_campus_doutorado.append(b)
    
    print(f"Bolsistas 'NÃO INFORMADO' encontrados:")
    print(f"  Mestrado:  {len(sem_campus_mestrado)}")
    print(f"  Doutorado: {len(sem_campus_doutorado)}")
    print(f"  Total:     {len(sem_campus_mestrado) + len(sem_campus_doutorado)}\n")
    
    print(f"Relatório mostra: 28M + 18D = 46 total\n")
    
    if len(sem_campus_mestrado) == 28 and len(sem_campus_doutorado) == 18:
        print("NÚMEROS CONFEREM!\n")
    else:
        diff_m = len(sem_campus_mestrado) - 28
        diff_d = len(sem_campus_doutorado) - 18
        print(f"DIVERGÊNCIA: {diff_m:+d}M, {diff_d:+d}D\n")
    
    # LISTAR MESTRADO
    if sem_campus_mestrado:
        print("=" * 90)
        print(f"MESTRADO ({len(sem_campus_mestrado)} bolsistas)")
        print("=" * 90)
        for idx, b in enumerate(sem_campus_mestrado, 1):
            programa_txt = b.programa or (b.programa_link.nome_programa if b.programa_link else 'SEM PROGRAMA')
            print(f"{idx:2d}. {b.nome:45s} | CPF: {b.cpf:15s} | {programa_txt[:40]}")
        print()
    
    if sem_campus_doutorado:
        print("=" * 90)
        print(f"DOUTORADO ({len(sem_campus_doutorado)} bolsistas)")
        print("=" * 90)
        for idx, b in enumerate(sem_campus_doutorado, 1):
            programa_txt = b.programa or (b.programa_link.nome_programa if b.programa_link else 'SEM PROGRAMA')
            print(f"{idx:2d}. {b.nome:45s} | CPF: {b.cpf:15s} | {programa_txt[:40]}")
