"""
Lista bolsistas sem campus definido
Mostra nome, CPF e nível (Mestrado/Doutorado)
"""

from app import app, db
from models import Bolsista

with app.app_context():
    print("=== BOLSISTAS SEM CAMPUS DEFINIDO ===\n")
    
    # Buscar TODOS os bolsistas
    bolsistas = Bolsista.query.all()
    
    # Filtrar aqueles sem campus
    sem_campus = {'M': [], 'D': []}
    
    for b in bolsistas:
        # Determinar campus
        if b.programa_link and b.programa_link.campus:
            continue  # Tem campus via programa_link
        elif b.programa and '(' in b.programa:
            continue  # Tem campus no campo texto (ex: "PPGEM (CT)")
        
        # Se chegou aqui, NÃO tem campus
        if not b.modalidade:
            continue
        
        nivel_raw = b.modalidade.nivel.upper()
        if 'MESTRADO' in nivel_raw or 'MASTER' in nivel_raw or nivel_raw == 'M':
            nivel = 'M'
        elif 'DOUTORADO' in nivel_raw or 'DOCTOR' in nivel_raw or 'PHD' in nivel_raw or nivel_raw == 'D':
            nivel = 'D'
        else:
            continue
        
        sem_campus[nivel].append({
            'nome': b.nome,
            'cpf': b.cpf if b.cpf else 'NÃO CADASTRADO',
            'programa': b.programa if b.programa else 'NÃO INFORMADO'
        })
    
    # Exibir MESTRADO
    print(f"📋 MESTRADO: {len(sem_campus['M'])} bolsistas\n")
    print(f"{'#':<4} {'NOME':<40} {'CPF':<15} PROGRAMA")
    print("-" * 100)
    
    for i, b in enumerate(sem_campus['M'], 1):
        print(f"{i:<4} {b['nome']:<40} {b['cpf']:<15} {b['programa']}")
    
    print(f"\n{'=' * 100}\n")
    
    # Exibir DOUTORADO
    print(f"📋 DOUTORADO: {len(sem_campus['D'])} bolsistas\n")
    print(f"{'#':<4} {'NOME':<40} {'CPF':<15} PROGRAMA")
    print("-" * 100)
    
    for i, b in enumerate(sem_campus['D'], 1):
        print(f"{i:<4} {b['nome']:<40} {b['cpf']:<15} {b['programa']}")
    
    print(f"\n{'=' * 100}")
    print(f"\n📊 TOTAL: {len(sem_campus['M']) + len(sem_campus['D'])} bolsistas sem campus")
    print(f"   - Mestrado: {len(sem_campus['M'])}")
    print(f"   - Doutorado: {len(sem_campus['D'])}")
