"""
Script SIMPLIFICADO para cadastrar cotas IES
Usando SQL direto sem parâmetros nomeados
"""

from app import app, db

with app.app_context():
    print("=== CADASTRANDO COTAS IES ===\n")
    
    # Buscar IDs das modalidades IES (Edital 13)
    result = db.session.execute(db.text("""
        SELECT id, nivel 
        FROM modalidades 
        WHERE edital_id = 13
    """))
    
    mod_m_id = None
    mod_d_id = None
    
    for row in result:
        if 'Mestrado' in row[1]:
            mod_m_id = row[0]
        elif 'Doutorado' in row[1]:
            mod_d_id = row[1]
    
    if not mod_m_id or not mod_d_id:
        print("ERRO: Modalidades IES nao encontradas!")
        exit(1)
    
    print(f"Modalidade Mestrado IES: ID {mod_m_id}")
    print(f"Modalidade Doutorado IES: ID {mod_d_id}\n")
    
    # Remover cotas IES existentes
    db.session.execute(db.text("""
        DELETE FROM distribuicao_cotas 
        WHERE edital_id = 13 AND programa_id IS NULL
    """))
    
    # Inserir cotas IES Mestrado (14)
    db.session.execute(db.text(f"""
        INSERT INTO distribuicao_cotas 
        (edital_id, modalidade_id, programa_id, qtd_concedida)
        VALUES (13, {mod_m_id}, NULL, 14)
    """))
    
    print("✅ Cadastrado: 14 cotas Mestrado IES")
    
    # Inserir cotas IES Doutorado (9)
    db.session.execute(db.text(f"""
        INSERT INTO distribuicao_cotas 
        (edital_id, modalidade_id, programa_id, qtd_concedida)
        VALUES (13, {mod_d_id}, NULL, 9)
    """))
    
    print("✅ Cadastrado: 9 cotas Doutorado IES")
    
    db.session.commit()
    
    # Verificar
    print("\n=== VERIFICACAO ===\n")
    
    result = db.session.execute(db.text("""
        SELECT m.nivel, SUM(dc.qtd_concedida)
        FROM distribuicao_cotas dc
        JOIN modalidades m ON dc.modalidade_id = m.id
        WHERE dc.edital_id IN (13, 14)
        GROUP BY m.nivel
    """))
    
    for row in result:
        print(f"{row[0]}: {row[1]} cotas")
    
    print("\n✅ Cotas IES cadastradas com sucesso!")
