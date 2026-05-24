import sys
import os
import logging
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import DadosFinanceiros

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def insert_financial_data():
    print("--- Inserting Financial Data (2025 Report) ---")
    with app.app_context():
        # Source: User Prompt / Management Report
        # Total: R$ 22.154.895,86
        # Breakdown: CNPq (12.4M), Araucária (6.1M), FINEP (3.4M)
        
        data = [
            {'ano': 2025, 'categoria': 'Captação Externa - CNPq', 'valor': 12400000.00, 'descricao': 'Projetos e Bolsas CNPq'},
            {'ano': 2025, 'categoria': 'Captação Externa - Fundação Araucária', 'valor': 6100000.00, 'descricao': 'Fomento Estadual'},
            {'ano': 2025, 'categoria': 'Captação Externa - FINEP', 'valor': 3400000.00, 'descricao': 'Infraestrutura e Projetos FINEP'},
            {'ano': 2025, 'categoria': 'Captação Externa - Outros', 'valor': 254895.86, 'descricao': 'Outras fontes (Compensação para totalizar 22.15M)'}
        ]
        
        count = 0
        for item in data:
            # Check exist
            exists = DadosFinanceiros.query.filter_by(ano=item['ano'], categoria=item['categoria']).first()
            if not exists:
                new_rec = DadosFinanceiros(
                    ano=item['ano'],
                    categoria=item['categoria'],
                    valor=item['valor'],
                    descricao=item['descricao']
                )
                db.session.add(new_rec)
                count += 1
            else:
                exists.valor = item['valor'] # Update value just in case
        
        db.session.commit()
        print(f"[SUCCESS] Inserted/Updated {count} financial records.")

if __name__ == "__main__":
    insert_financial_data()
