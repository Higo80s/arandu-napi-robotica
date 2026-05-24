import os
import sys
from datetime import date

# Garantir que o diretório raiz esteja no PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Bolsista

def analyze_old_bolsas():
    target_date = date(2026, 2, 1) # February 2026
    
    with app.app_context():
        # A página de /alertas usa: data_fim_bolsa < hoje AND ativo == True
        # Nós filtramos os que são anteriores a Fevereiro de 2026
        bolsistas = Bolsista.query.filter(
            Bolsista.data_fim_bolsa < target_date,
            Bolsista.ativo == True
        ).all()
        
        print(f"Total de bolsistas ativos com vencimento ANTERIOR a {target_date.strftime('%d/%m/%Y')}: {len(bolsistas)}")
        
        for b in bolsistas:
             # Just print some sample info
             prog_nome = b.programa_link.sigla_programa if b.programa_link else (b.programa or '-')
             ed_nome = b.edital.numero if b.edital else '-'
             print(f" - {b.nome} | Edital: {ed_nome} | Fim: {b.data_fim_bolsa.strftime('%d/%m/%Y')} | Prog: {prog_nome}")

if __name__ == '__main__':
    analyze_old_bolsas()
