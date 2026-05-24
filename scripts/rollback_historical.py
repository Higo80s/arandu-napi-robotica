import sys
import os
from sqlalchemy import text

# Contexto da Aplicação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import BolsaVolumetriaAnual

def run():
    print("--- INICIANDO ROLLBACK DE DADOS HISTÓRICOS ---")
    with app.app_context():
        try:
            # Opção 1: Usar ORM
            num_deleted = db.session.query(BolsaVolumetriaAnual).delete()
            
            # Opção 2: Truncate (mais rápido, mas específico do banco)
            # db.session.execute(text("TRUNCATE TABLE bolsa_volumetria_anual RESTART IDENTITY CASCADE;"))
            
            db.session.commit()
            print(f"SUCESSO: {num_deleted} registros foram removidos da tabela 'bolsa_volumetria_anual'.")
            print("A tabela agora está vazia. Nenhum dado de bolsista ativo foi afetado.")
            
        except Exception as e:
            db.session.rollback()
            print(f"ERRO durante rollback: {e}")

if __name__ == '__main__':
    run()
