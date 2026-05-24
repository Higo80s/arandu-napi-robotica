from app import app, db, Bolsista
from sqlalchemy import text

def add_registro_academico():
    with app.app_context():
        # Check if column exists
        result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='bolsistas' AND column_name='registro_academico'"))
        if not result.fetchone():
            print("Adicionando coluna 'registro_academico' à tabela 'bolsistas'...")
            db.session.execute(text("ALTER TABLE bolsistas ADD COLUMN registro_academico VARCHAR(50) UNIQUE"))
            db.session.commit()
            print("Coluna adicionada com sucesso!")
        else:
            print("A coluna 'registro_academico' já existe.")

if __name__ == '__main__':
    add_registro_academico()
