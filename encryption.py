from sqlalchemy.types import TypeDecorator, String
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

key = os.getenv('ENCRYPTION_KEY')
cipher_suite = Fernet(key.encode()) if key else None

class EncryptedString(TypeDecorator):
    """
    Tipo SQLAlchemy que criptografa dados ao salvar e descriptografa ao ler.
    Usa Fernet (criptografia simétrica).
    """
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Criptografa o valor antes de salvar no banco."""
        if not value:
            return None
        if not cipher_suite:
            return value # Se não houver chave, salva em texto plano (fallback)
            
        if isinstance(value, str):
            value = value.encode('utf-8')
            
        encrypted_value = cipher_suite.encrypt(value)
        return encrypted_value.decode('utf-8')

    def process_result_value(self, value, dialect):
        """Descriptografa o valor ao ler do banco."""
        if not value:
            return None
        if not cipher_suite:
            return value

        try:
            decrypted_value = cipher_suite.decrypt(value.encode('utf-8'))
            return decrypted_value.decode('utf-8')
        except Exception:
            # Se falhar (ex: dado legado não criptografado), retorna o valor original
            return value
