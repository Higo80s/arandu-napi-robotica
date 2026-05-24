"""
EXTENSIONS.PY
=============
Centraliza a instanciamento de extensões do Flask para evitar dependências circulares.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

# Instanciar extensões (sem app por enquanto)
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()

# [V11.2] Gestão de Criptografia (Fernet)
_cipher_suite = None

def get_cipher_suite():
    """Garante que o cipher_suite seja um Singleton acessível em todo o app."""
    global _cipher_suite
    if _cipher_suite is None:
        from cryptography.fernet import Fernet
        import os
        from dotenv import load_dotenv
        
        # Load env if not already loaded (failsafe)
        load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
        
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
             # Se falhar no env, tenta fallback ou loga erro
             print(" [CRITICAL] ENCRYPTION_KEY não encontrada no .env")
             return None
        _cipher_suite = Fernet(key.encode())
    return _cipher_suite

# Atalho para importação limpa
cipher_suite = get_cipher_suite()
