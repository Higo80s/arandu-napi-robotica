"""
Lista os 3 bolsistas NÃO INFORMADO
Apenas nome e CPF
"""

from app import app
from models import Bolsista

with app.app_context():
    nao_informado = []
    
    # CAPES IES ativos
    ies = Bolsista.query.filter_by(edital_id=13, ativo=True).all()
    for b in ies:
        if not (b.programa_link and b.programa_link.campus) and not (b.programa and '(' in b.programa):
            nao_informado.append(b)
    
    # Outros editais ativos
    outros = Bolsista.query.filter(
        Bolsista.ativo == True,
        Bolsista.edital_id.notin_([13, 14])
    ).all()
    
    for b in outros:
        if not (b.programa_link and b.programa_link.campus) and not (b.programa and '(' in b.programa):
            nao_informado.append(b)
    
    print("=== 3 BOLSISTAS 'NAO INFORMADO' ===\n")
    
    for idx, b in enumerate(nao_informado, 1):
        nivel = b.modalidade.nivel if b.modalidade else 'N/A'
        edital = b.edital.numero if b.edital else 'N/A'
        
        output = f"{idx}. {b.nome}\n   CPF: {b.cpf}\n   Nivel: {nivel}\n   Edital: {edital}\n"
        print(output)
        
    # Salvar em arquivo
    with open('lista_3_bolsistas.txt', 'w', encoding='utf-8') as f:
        f.write("=== 3 BOLSISTAS 'NAO INFORMADO' ===\n\n")
        for idx, b in enumerate(nao_informado, 1):
            nivel = b.modalidade.nivel if b.modalidade else 'N/A'
            edital = b.edital.numero if b.edital else 'N/A'
            f.write(f"{idx}. {b.nome}\n")
            f.write(f"   CPF: {b.cpf}\n")
            f.write(f"   Nivel: {nivel}\n")
            f.write(f"   Edital: {edital}\n\n")
    
    print("\n✅ Lista salva em lista_3_bolsistas.txt")
