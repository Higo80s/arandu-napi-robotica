"""
Script para cadastrar cotas CAPES IES e ajustar DS
Baseado nos dados oficiais fornecidos
"""

from app import app, db
from models import Edital, Modalidade
from sqlalchemy import text

with app.app_context():
    print("=== CORRECAO COTAS CAPES ===\n")
    
    # 1. Buscar editais e modalidades (IDs 13 e 14)
    edital_ies = Edital.query.get(13)  # CAPES DS (IES)
    edital_ds = Edital.query.get(14)   # CAPES DS
    
    if not edital_ds or not edital_ies:
        print("ERRO: Editais CAPES nao encontrados!")
        exit(1)
    
    print(f"Edital DS: {edital_ds.numero} (ID {edital_ds.id})")
    print(f"Edital IES: {edital_ies.numero} (ID {edital_ies.id})\n")
    
    # Buscar modalidades de cada edital
    mod_m_ds = Modalidade.query.filter_by(edital_id=edital_ds.id).filter(
        Modalidade.nivel.ilike('%mestrado%')
    ).first()
    
    mod_d_ds = Modalidade.query.filter_by(edital_id=edital_ds.id).filter(
        Modalidade.nivel.ilike('%doutorado%')
    ).first()
    
    mod_m_ies = Modalidade.query.filter_by(edital_id=edital_ies.id).filter(
        Modalidade.nivel.ilike('%mestrado%')
    ).first()
    
    mod_d_ies = Modalidade.query.filter_by(edital_id=edital_ies.id).filter(
        Modalidade.nivel.ilike('%doutorado%')
    ).first()
    
    if not all([mod_m_ds, mod_d_ds, mod_m_ies, mod_d_ies]):
        print("ERRO: Modalidades nao encontradas!")
        print(f"  Mestrado DS: {mod_m_ds}")
        print(f"  Doutorado DS: {mod_d_ds}")
        print(f"  Mestrado IES: {mod_m_ies}")
        print(f"  Doutorado IES: {mod_d_ies}")
        exit(1)
    
    # 2. Cadastrar cotas IES rotativas (programa_id = NULL)
    print("=== CADASTRANDO COTAS IES ROTATIVAS ===\n")
    
    # Verificar se já existem
    sql_check = """
        SELECT COUNT(*) FROM distribuicao_cotas 
        WHERE edital_id = :edital_id AND programa_id IS NULL
    """
    
    count_ies = db.session.execute(
        text(sql_check), 
        {'edital_id': edital_ies.id}
    ).scalar()
    
    if count_ies > 0:
        print(f"Ja existem {count_ies} cotas IES cadastradas.")
        print("Removendo para recadastrar...\n")
        
        sql_delete = """
            DELETE FROM distribuicao_cotas 
            WHERE edital_id = :edital_id AND programa_id IS NULL
        """
        db.session.execute(text(sql_delete), {'edital_id': edital_ies.id})
    
    # Inserir cotas IES
    sql_insert = """
        INSERT INTO distribuicao_cotas 
        (edital_id, modalidade_id, programa_id, qtd_concedida)
        VALUES (:edital, :modalidade, NULL, :qtd)
    """
    
    # Mestrado IES: 14 cotas
    db.session.execute(text(sql_insert), {
        'edital': edital_ies.id,
        'modalidade': mod_m_ies.id,
        'qtd': 14
    })
    print("✅ Cadastrado: 14 cotas Mestrado IES (rotativas)")
    
    # Doutorado IES: 9 cotas
    db.session.execute(text(sql_insert), {
        'edital': edital_ies.id,
        'modalidade': mod_d_ies.id,
        'qtd': 9
    })
    print("✅ Cadastrado: 9 cotas Doutorado IES (rotativas)")
    
    db.session.commit()
    
    # 3. Verificar totais
    print("\n=== VERIFICACAO FINAL ===\n")
    
    sql_total = """
        SELECT 
            m.nivel,
            SUM(dc.qtd_concedida) as total
        FROM distribuicao_cotas dc
        JOIN modalidades m ON dc.modalidade_id = m.id
        WHERE dc.edital_id IN (:ds, :ies)
        GROUP BY m.nivel
    """
    
    result = db.session.execute(text(sql_total), {
        'ds': edital_ds.id,
        'ies': edital_ies.id
    })
    
    total_m = 0
    total_d = 0
    
    for row in result:
        nivel = row[0]
        total = row[1]
        
        if 'Mestrado' in nivel:
            total_m += total
            print(f"Mestrado: {total}")
        elif 'Doutorado' in nivel:
            total_d += total
            print(f"Doutorado: {total}")
    
    print(f"\nTOTAL:")
    print(f"  Mestrado:  {total_m} (Esperado: 269)")
    print(f"  Doutorado: {total_d} (Esperado: 160)")
    print(f"  Total:     {total_m + total_d} (Esperado: 429)")
    
    if total_m == 269 and total_d == 160:
        print("\n✅ COTAS CORRETAS!")
    else:
        diff_m = total_m - 269
        diff_d = total_d - 160
        print(f"\n⚠️  Diferenca:")
        print(f"  Mestrado:  {diff_m:+d}")
        print(f"  Doutorado: {diff_d:+d}")
