"""
Identifica os 3 bolsistas "NÃO INFORMADO" do novo relatório
E explica o que cada um representa
"""

from app import app, db
from models import Bolsista
from sqlalchemy import text

with app.app_context():
    print("=== ANÁLISE 'NÃO INFORMADO' - 3 BOLSISTAS ===\n")
    
    # Replicar EXATA lógica do novo relatório
    nao_informado_m = []
    nao_informado_d = []
    
    # 1. CAPES DS (Edital 14) - Cotas da tabela, não bolsistas individuais
    # Não contribui para "NÃO INFORMADO" pois usa distribuicao_cotas
    
    # 2. CAPES IES (Edital 13) - Bolsistas ativos
    bolsistas_ies = Bolsista.query.filter_by(edital_id=13, ativo=True).all()
    
    for b in bolsistas_ies:
        if b.programa_link and b.programa_link.campus:
            continue
        elif b.programa and '(' in b.programa:
            continue
        else:
            # NÃO INFORMADO!
            if b.modalidade:
                nivel = b.modalidade.nivel.upper()
                if 'MESTRADO' in nivel:
                    nao_informado_m.append(('IES', b))
                elif 'DOUTORADO' in nivel:
                    nao_informado_d.append(('IES', b))
    
    # 3. Outros editais - Bolsistas ativos
    outros = Bolsista.query.filter(
        Bolsista.ativo == True,
        Bolsista.edital_id.notin_([13, 14])
    ).all()
    
    for b in outros:
        if b.programa_link and b.programa_link.campus:
            continue
        elif b.programa and '(' in b.programa:
            continue
        else:
            # NÃO INFORMADO!
            if b.modalidade:
                nivel = b.modalidade.nivel.upper()
                if 'MESTRADO' in nivel or 'MASTER' in nivel:
                    nao_informado_m.append(('OUTROS', b))
                elif 'DOUTORADO' in nivel or 'DOCTOR' in nivel:
                    nao_informado_d.append(('OUTROS', b))
    
    print(f"Total: {len(nao_informado_m)}M + {len(nao_informado_d)}D = {len(nao_informado_m) + len(nao_informado_d)}\n")
    
    # LISTAR MESTRADO
    if nao_informado_m:
        print("MESTRADO - {} bolsista(s)".format(len(nao_informado_m)))
        print("=" * 90)
        for origem, b in nao_informado_m:
            edital_nome = b.edital.numero if b.edital else 'SEM EDITAL'
            programa_txt = b.programa or (b.programa_link.nome_programa if b.programa_link else 'SEM PROGRAMA')
            print(f"  Nome: {b.nome}")
            print(f"  CPF: {b.cpf}")
            print(f"  Edital: {edital_nome} ({origem})")
            print(f"  Programa: {programa_txt}")
            print(f"  Status campo campus: {b.campus if b.campus else 'VAZIO'}")
            print(f"  Status programa_link: {'SIM' if b.programa_link else 'NÃO'}")
            if b.programa_link:
                print(f"    - Campus do programa_link: {'SIM' if b.programa_link.campus else 'NÃO'}")
            print()
    
    # LISTAR DOUTORADO
    if nao_informado_d:
        print("DOUTORADO - {} bolsista(s)".format(len(nao_informado_d)))
        print("=" * 90)
        for origem, b in nao_informado_d:
            edital_nome = b.edital.numero if b.edital else 'SEM EDITAL'
            programa_txt = b.programa or (b.programa_link.nome_programa if b.programa_link else 'SEM PROGRAMA')
            print(f"  Nome: {b.nome}")
            print(f"  CPF: {b.cpf}")
            print(f"  Edital: {edital_nome} ({origem})")
            print(f"  Programa: {programa_txt}")
            print(f"  Status campo campus: {b.campus if b.campus else 'V AZIO'}")
            print(f"  Status programa_link: {'SIM' if b.programa_link else 'NÃO'}")
            if b.programa_link:
                print(f"    - Campus do programa_link: {'SIM' if b.programa_link.campus else 'NÃO'}")
            print()
    
    print("=" * 90)
    print("\nCONCLUSÃO:")
    print("'NÃO INFORMADO' = Bolsistas ATIVOS que:")
    print("  1. NÃO têm programa_link.campus definido")
    print("  2. E NÃO têm campus no campo texto 'programa' (ex: 'PPGEM (CT)')")
    print("\nSão bolsas IMPLEMENTADAS (ativas) mas SEM CAMPUS atribuído no sistema.")
