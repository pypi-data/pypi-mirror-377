from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

def encrypt_message(message: str, key: bytes) -> str:
    cipher = AES.new(key, AES.MODE_GCM)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(message.encode())
    return base64.b64encode(nonce + ciphertext + tag).decode('utf-8')

def decrypt_message(encrypted_message: str, key: bytes) -> str:
    raw_data = base64.b64decode(encrypted_message.encode('utf-8'))
    nonce, ciphertext, tag = raw_data[:16], raw_data[16:-16], raw_data[-16:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
