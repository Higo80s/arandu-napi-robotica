"""
Cadastra cotas IES usando ORM (evita problemas com NULL)
"""

from app import app, db
from models import DistribuicaoCotas, Modalidade

with app.app_context():
    print("=== CADASTRANDO COTAS IES ===\n")
    
    # Buscar modalidades IES (Edital 13)
    mod_m_ies = Modalidade.query.filter_by(edital_id=13).filter(
        Modalidade.nivel.ilike('%mestrado%')
    ).first()
    
    mod_d_ies = Modalidade.query.filter_by(edital_id=13).filter(
        Modalidade.nivel.ilike('%doutorado%')
    ).first()
    
    if not mod_m_ies or not mod_d_ies:
        print("ERRO: Modalidades IES nao encontradas!")
        exit(1)
    
    print(f"Modalidade Mestrado IES: {mod_m_ies.nivel} (ID {mod_m_ies.id})")
    print(f"Modalidade Doutorado IES: {mod_d_ies.nivel} (ID {mod_d_ies.id})\n")
    
    # Remover cotas IES existentes
    DistribuicaoCotas.query.filter_by(
        edital_id=13,
        programa_id=None
    ).delete()
    
    # Criar cotas IES Mestrado (14)
    cota_m = DistribuicaoCotas(
        edital_id=13,
        modalidade_id=mod_m_ies.id,
        programa_id=None,  # Rotativa
        qtd_concedida=14
    )
    db.session.add(cota_m)
    print("✅ Criado: 14 cotas Mestrado IES (rotativas)")
    
    # Criar cotas IES Doutorado (9)
    cota_d = DistribuicaoCotas(
        edital_id=13,
        modalidade_id=mod_d_ies.id,
        programa_id=None,  # Rotativa
        qtd_concedida=9
    )
    db.session.add(cota_d)
    print("✅ Criado: 9 cotas Doutorado IES (rotativas)")
    
    db.session.commit()
    
    # Verificar totais
    print("\n=== VERIFICACAO FINAL ===\n")
    
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
    
    print(f"\nRESUMO:")
    print(f"  Mestrado:  {total_m} (Esperado: 269)")
    print(f"  Doutorado: {total_d} (Esperado: 160)")
    print(f"  Total:     {total_m + total_d} (Esperado: 429)")
    
    if total_m == 269 and total_d == 160:
        print("\n✅ PERFEITO! Cotas batem com oficial CAPES!")
    else:
        print(f"\n⚠️  Diferenca: M {total_m-269:+d}, D {total_d-160:+d}")
