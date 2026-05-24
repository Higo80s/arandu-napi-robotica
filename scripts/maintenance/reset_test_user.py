"""
RESET USER DE TESTE
===================
Reseta o usuário viewer@utfpr.edu.br para o estado inicial de teste.
"""
from app import app, db
from models import User
from dotenv import load_dotenv

load_dotenv()

with app.app_context():
    u = User.query.filter_by(email='viewer@utfpr.edu.br').first()
    if u:
        print(f"Resetando usuário {u.email}...")
        u.set_password('123')
        u.must_change_password = True
        db.session.commit()
        print("✅ Usuário resetado: Senha '123' e Flag TRUE")
    else:
        print("❌ Usuário não encontrado.")
