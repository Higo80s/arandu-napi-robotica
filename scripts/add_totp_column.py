from app import app, db
from sqlalchemy import text

def add_totp_column():
    print("🔐 Adicionando coluna 'totp_secret' para 2FA...")
    with app.app_context():
        try:
            # Verifica se a coluna já existe
            check_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name='usuarios' AND column_name='totp_secret'")
            result = db.session.execute(check_sql).fetchone()
            
            if result:
                print("⚠️ Coluna 'totp_secret' já existe.")
                return

            sql = text("ALTER TABLE usuarios ADD COLUMN totp_secret VARCHAR(32);")
            db.session.execute(sql)
            db.session.commit()
            print("✅ Sucesso! Coluna 'totp_secret' adicionada.")
            
        except Exception as e:
            print(f"❌ Erro ao adicionar coluna: {e}")
            db.session.rollback()

if __name__ == "__main__":
    add_totp_column()
