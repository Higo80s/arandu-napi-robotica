from app import app
from models import User
from extensions import db

with app.app_context():
    user = User.query.filter_by(email='higosantos@utfpr.edu.br').first()
    if user:
        user.set_password('Admin@2026Secure')
        user.totp_secret = None  # Disable 2FA in case that was also preventing access
        db.session.commit()
        print(f"Senha de {user.email} resetada com sucesso para: Admin@2026Secure")
    else:
        print("Usuário não encontrado.")
