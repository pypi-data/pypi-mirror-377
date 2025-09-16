import hashlib
import os
import base64
import secrets

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    pwdhash = base64.b64encode(pwdhash).decode('utf-8')
    salt = base64.b64encode(salt).decode('utf-8')
    return f"{salt}${pwdhash}"

def verify_password(stored_password: str, provided_password: str) -> bool:
    salt, stored_pwdhash = stored_password.split('$')
    salt = base64.b64decode(salt)
    pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt, 100000)
    pwdhash = base64.b64encode(pwdhash).decode('utf-8')
    return pwdhash == stored_pwdhash

def generate_password(length: int = 12) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_"
    return ''.join(secrets.choice(alphabet) for i in range(length))
