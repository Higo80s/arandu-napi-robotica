import sys
import os

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from sqlalchemy import text

def add_columns():
    with app.app_context():
        # Ensure new tables exist first
        db.create_all()
        print("Tabelas garantidas via db.create_all()")
        
        with db.engine.connect() as conn:
            # Check if column exists
            try:
                # PostgreSQL check
                result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='editais' AND column_name='agencia_id';"))
                if result.fetchone():
                    print("Coluna agencia_id já existe em editais.")
                else:
                    print("Adicionando coluna agencia_id em editais...")
                    conn.execute(text("ALTER TABLE editais ADD COLUMN agencia_id INTEGER REFERENCES agencias_fomento(id);"))
                    conn.commit()
                    print("Coluna agencia_id adicionada com sucesso.")
            except Exception as e:
                print(f"Erro ao verificar/adicionar coluna: {e}")

if __name__ == "__main__":
    add_columns()
