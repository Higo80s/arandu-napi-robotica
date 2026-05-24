"""
Gera lista completa dos bolsistas NÃO INFORMADO
com formato limpo para o chat
"""

from app import app
from models import Bolsista

with app.app_context():
    # Buscar TODOS bolsistas
    bolsistas = Bolsista.query.all()
    
    # Separar os "NÃO INFORMADO" usando lógica do relatório
    sem_campus_mestrado = []
    sem_campus_doutorado = []
    
    for b in bolsistas:
        if b.programa_link and b.programa_link.campus:
            continue
        elif b.programa and '(' in b.programa:
            continue
        else:
            if not b.modalidade:
                continue
            
            nivel = b.modalidade.nivel.upper()
            if 'MESTRADO' in nivel or 'MASTER' in nivel:
                sem_campus_mestrado.append(b)
            elif 'DOUTORADO' in nivel or 'DOCTOR' in nivel or 'PHD' in nivel:
                sem_campus_doutorado.append(b)
    
    print("MESTRADO - 28 BOLSISTAS")
    print("=" * 70)
    for idx, b in enumerate(sem_campus_mestrado, 1):
        print(f"{idx:2d}. {b.nome:45s} CPF: {b.cpf}")
    
    print("\n" + "=" * 70)
    print("DOUTORADO - 18 BOLSISTAS")
    print("=" * 70)
    for idx, b in enumerate(sem_campus_doutorado, 1):
        print(f"{idx:2d}. {b.nome:45s} CPF: {b.cpf}")
    
    print("\n" + "=" * 70)
    print(f"TOTAL: {len(sem_campus_mestrado) + len(sem_campus_doutorado)} bolsistas")
