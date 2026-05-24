from app import app, db
from sqlalchemy import text

def alter_columns():
    print("🔧 Alterando colunas para suportar criptografia (VARCHAR 255)...")
    with app.app_context():
        commands = [
            "ALTER TABLE bolsistas ALTER COLUMN cpf TYPE VARCHAR(255);",
            "ALTER TABLE bolsistas ALTER COLUMN agencia TYPE VARCHAR(255);",
            "ALTER TABLE bolsistas ALTER COLUMN conta TYPE VARCHAR(255);",
            "ALTER TABLE residentes ALTER COLUMN cpf TYPE VARCHAR(255);",
            "ALTER TABLE candidaturas ALTER COLUMN cpf TYPE VARCHAR(255);",
        ]
        
        try:
            for cmd in commands:
                print(f"Executando: {cmd}")
                db.session.execute(text(cmd))
            
            db.session.commit()
            print("✅ Sucesso! Colunas alteradas.")
        except Exception as e:
            print(f"❌ Erro ao alterar colunas: {e}")
            db.session.rollback()

if __name__ == "__main__":
    alter_columns()
