import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import User
from extensions import db

def reset_passwords():
    with app.app_context():
        users = User.query.all()
        print(f"Encontrados {len(users)} usuarios.")
        
        default_password = "Senha@Padrao2026!"
        
        success_count = 0
        error_count = 0
        cleared_2fa = 0
        
        for user in users:
            try:
                user.set_password(default_password)
                user.must_change_password = True
                
                # Desabilita 2FA se estiver habilitado
                if user.totp_secret:
                    user.totp_secret = None
                    cleared_2fa += 1
                    
                success_count += 1
            except Exception as e:
                print(f"Erro ao redefinir a senha de {user.email}: {e}")
                error_count += 1
                
        try:
            db.session.commit()
            print(f"Senhas redefinidas com sucesso para {success_count} usuarios.")
            print(f"2FA desabilitado para {cleared_2fa} usuarios.")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao salvar no banco de dados: {e}")

if __name__ == "__main__":
    reset_passwords()
