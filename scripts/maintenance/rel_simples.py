"""
Relatorio SIMPLES sem caracteres especiais
"""

from app import app
from models import Bolsista, Edital

with app.app_context():
    print("ANALISE DISCREPANCIA CAPES")
    print("=" * 50)
    
    total = Bolsista.query.filter_by(ativo=True).count()
    print(f"\nTotal sistema: {total}")
    print(f"Total oficial CAPES: 429")
    print(f"Diferenca: +{total - 429}")
    
    print("\n" + "=" * 50)
    print("BOLSISTAS POR EDITAL")
    print("=" * 50)
    
    for e in Edital.query.all():
        count = Bolsista.query.filter_by(edital_id=e.id, ativo=True).count()
        if count > 0:
            clean_numero = e.numero.replace('\u00e7', 'c').replace('\u00e3', 'a')
            clean_agencia = e.agencia.replace('\u00e7', 'c').replace('\u00e3', 'a')
            print(f"{clean_numero[:35]:35s} | {clean_agencia[:10]:10s} | {count:3d}")
