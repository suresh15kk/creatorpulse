from cryptography.fernet import Fernet
from app.core.config import get_settings
import base64

settings = get_settings()

def _get_cipher():
    key = settings.encryption_key.encode()
    key = key[:32].ljust(32, b'0')
    encoded = base64.urlsafe_b64encode(key)
    return Fernet(encoded)

def encrypt_token(token: str) -> str:
    return _get_cipher().encrypt(token.encode()).decode()

def decrypt_token(encrypted: str) -> str:
    return _get_cipher().decrypt(encrypted.encode()).decode()