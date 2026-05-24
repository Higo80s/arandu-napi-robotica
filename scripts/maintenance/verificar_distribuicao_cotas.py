"""
Script para verificar distribuição atual de cotas CAPES DS
E identificar discrepâncias
"""

from app import app, db
from sqlalchemy import text

with app.app_context():
    print("=== VERIFICACAO COTAS DS/PPG (Edital 14) ===\n")
    
    # Cotas DS/PPG por nível
    sql = """
        SELECT 
            m.nivel,
            SUM(dc.qtd_concedida) as total,
            COUNT(DISTINCT dc.programa_id) as programas
        FROM distribuicao_cotas dc
        JOIN modalidades m ON dc.modalidade_id = m.id
        WHERE dc.edital_id = 14 AND dc.programa_id IS NOT NULL
        GROUP BY m.nivel
    """
    
    result = db.session.execute(text(sql))
    
    total_m = 0
    total_d = 0
    
    print("Cotas DS/PPG por nivel:")
    for row in result:
        nivel = row[0]
        total = row[1]
        progs = row[2]
        
        print(f"  {nivel}: {total} cotas em {progs} programas")
        
        if 'Mestrado' in nivel:
            total_m += total
        elif 'Doutorado' in nivel:
            total_d += total
    
    print(f"\nTOTAL DS/PPG:")
    print(f"  Mestrado:  {total_m} (Esperado: 255)")
    print(f"  Doutorado: {total_d} (Esperado: 151)")
    print(f"  Total:     {total_m + total_d} (Esperado: 406)")
    
    # Verificar cotas IES
    print("\n=== VERIFICACAO COTAS IES (Edital 13) ===\n")
    
    sql_ies = """
        SELECT 
            m.nivel,
            SUM(dc.qtd_concedida) as total
        FROM distribuicao_cotas dc
        JOIN modalidades m ON dc.modalidade_id = m.id
        WHERE dc.edital_id = 13
        GROUP BY m.nivel
    """
    
    result_ies = db.session.execute(text(sql_ies))
    
    total_m_ies = 0
    total_d_ies = 0
    
    print("Cotas IES:")
    for row in result_ies:
        nivel = row[0]
        total = row[1]
        
        print(f"  {nivel}: {total} cotas")
        
        if 'Mestrado' in nivel:
            total_m_ies += total
        elif 'Doutorado' in nivel:
            total_d_ies += total
    
    print(f"\nTOTAL IES:")
    print(f"  Mestrado:  {total_m_ies} (Esperado: 14)")
    print(f"  Doutorado: {total_d_ies} (Esperado: 9)")
    print(f"  Total:     {total_m_ies + total_d_ies} (Esperado: 23)")
    
    # Total geral
    print("\n=== TOTAL GERAL CAPES ===\n")
    total_geral = total_m + total_d + total_m_ies + total_d_ies
    print(f"Sistema:  {total_geral} cotas")
    print(f"Oficial:  429 cotas")
    print(f"Diferenca: {total_geral - 429:+d}")
