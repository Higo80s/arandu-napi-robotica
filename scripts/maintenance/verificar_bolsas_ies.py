"""Verificar bolsistas IES cadastrados no sistema"""
from app import app, db
from models import Bolsista
from sqlalchemy import text

with app.app_context():
    print("=" * 70)
    print("VERIFICAÇÃO DE BOLSAS IES")
    print("=" * 70)
    
    # 1. Bolsistas com agência IES
    print("\n1. Bolsistas cadastrados com agência 'IES':")
    bolsistas_ies = Bolsista.query.filter(Bolsista.agencia_fomento.contains('IES')).all()
    print(f"   Total: {len(bolsistas_ies)}")
    
    for b in bolsistas_ies:
        nivel = b.modalidade.nivel if b.modalidade else "?"
        status = "ATIVO" if b.ativo else "INATIVO"
        print(f"   - {b.nome} ({nivel}): {status}")
    
    # 2. Cotas IES no banco
    print("\n2. Cotas IES cadastradas (programa_id IS NULL):")
    sql = """
        SELECT m.nivel, dc.qtd_concedida
        FROM distribuicao_cotas dc
        JOIN modalidades m ON dc.modalidade_id = m.id
        WHERE dc.edital_id = 14 AND dc.programa_id IS NULL
    """
    result = db.session.execute(text(sql))
    total_cotas_ies = 0
    for row in result:
        print(f"   {row[0]}: {row[1]} cotas")
        total_cotas_ies += row[1]
    
    print(f"\n   Total cotas IES: {total_cotas_ies}")
    
    # 3. Comparação
    print("\n" + "=" * 70)
    print("ANÁLISE")
    print("=" * 70)
    print(f"Bolsistas IES cadastrados: {len(bolsistas_ies)}")
    print(f"Cotas IES disponíveis: {total_cotas_ies}")
    print(f"Diferença: {total_cotas_ies - len(bolsistas_ies)} cotas livres")
    print("=" * 70)
