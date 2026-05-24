from app import app
from models import Bolsista, Edital
from sqlalchemy import or_

with app.app_context():
    # 1. Buscar todos os bolsistas de agência CAPES ou editais CAPES
    bolsistas = Bolsista.query.join(Edital).filter(
        or_(
            Edital.numero.ilike('%CAPES%'),
            Edital.agencia.ilike('%CAPES%')
        ),
        Bolsista.ativo == True
    ).all()
    
    # 2. Agrupar por data_fim_bolsa
    vencimentos = {}
    for b in bolsistas:
        d = str(b.data_fim_bolsa)
        vencimentos[d] = vencimentos.get(d, 0) + 1
        
    # 3. Ordenar e imprimir
    print(f"Total bolsas CAPES ativas: {len(bolsistas)}")
    for d in sorted(vencimentos.keys()):
        print(f"Fim: {d} | Quantidade: {vencimentos[d]}")
