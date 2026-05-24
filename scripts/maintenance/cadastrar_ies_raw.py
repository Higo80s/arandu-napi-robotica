"""
Cadastra cotas IES usando conexão raw do SQLite
"""

from app import app, db

with app.app_context():
    print("=== CADASTRANDO COTAS IES ===\n")
    
    # Usar conexão raw do SQLite
    conn = db.engine.raw_connection()
    cursor = conn.cursor()
    
    # Buscar IDs das modalidades IES
    cursor.execute("""
        SELECT id, nivel FROM modalidades WHERE edital_id = 13
    """)
    
    mod_m_id = None
    mod_d_id = None
    
    for row in cursor.fetchall():
        if 'Mestrado' in row[1]:
            mod_m_id = row[0]
        elif 'Doutorado' in row[1]:
            mod_d_id = row[0]
    
    print(f"Modalidade Mestrado IES: ID {mod_m_id}")
    print(f"Modalidade Doutorado IES: ID {mod_d_id}\n")
    
    # Remover cotas IES existentes
    cursor.execute("""
        DELETE FROM distribuicao_cotas 
        WHERE edital_id = 13 AND programa_id IS NULL
    """)
    
    # Inserir Mestrado IES (14 cotas)
    cursor.execute("""
        INSERT INTO distribuicao_cotas 
        (edital_id, modalidade_id, programa_id, qtd_concedida)
        VALUES (?, ?, NULL, ?)
    """, (13, mod_m_id, 14))
    
    print("✅ Cadastrado: 14 cotas Mestrado IES")
    
    # Inserir Doutorado IES (9 cotas)
    cursor.execute("""
        INSERT INTO distribuicao_cotas 
        (edital_id, modalidade_id, programa_id, qtd_concedida)
        VALUES (?, ?, NULL, ?)
    """, (13, mod_d_id, 9))
    
    print("✅ Cadastrado: 9 cotas Doutorado IES")
    
    conn.commit()
    conn.close()
    
    # Verificar com SQLAlchemy
    print("\n=== VERIFICACAO ===\n")
    
    result = db.session.execute(db.text("""
        SELECT m.nivel, SUM(dc.qtd_concedida)
        FROM distribuicao_cotas dc
        JOIN modalidades m ON dc.modalidade_id = m.id
        WHERE dc.edital_id IN (13, 14)
        GROUP BY m.nivel
    """))
    
    total_m = 0
    total_d = 0
    
    for row in result:
        nivel = row[0]
        total = row[1]
        print(f"{nivel}: {total} cotas")
        
        if 'Mestrado' in nivel:
            total_m += total
        elif 'Doutorado' in nivel:
            total_d += total
    
    print(f"\nTOTAL:")
    print(f"  Mestrado:  {total_m} (Esperado: 269)")
    print(f"  Doutorado: {total_d} (Esperado: 160)")
    print(f"  Total:     {total_m + total_d} (Esperado: 429)")
    
    if total_m == 269 and total_d == 160:
        print("\n✅ PERFEITO! Numeros batem!")
    else:
        print(f"\n⚠️  Diferenca: M {total_m-269:+d}, D {total_d-160:+d}")
