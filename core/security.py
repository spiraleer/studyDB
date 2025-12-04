# core/security.py
import hashlib
import secrets

def hash_password(password: str) -> str:
    """Хеширует пароль с солью"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}:{password_hash.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль против хеша"""
    try:
        salt, stored_hash = hashed_password.split(':')
        password_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return password_hash.hex() == stored_hash
    except ValueError:
        return False

get_password_hash = hash_password