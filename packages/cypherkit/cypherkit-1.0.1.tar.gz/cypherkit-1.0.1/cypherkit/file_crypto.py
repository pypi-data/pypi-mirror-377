from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import os

def encrypt_file(file_path: str, password: str):
    salt = get_random_bytes(16)
    key = PBKDF2(password, salt, dkLen=32)
    cipher = AES.new(key, AES.MODE_GCM)
    nonce = cipher.nonce

    with open(file_path, 'rb') as f:
        data = f.read()

    ciphertext, tag = cipher.encrypt_and_digest(data)

    with open(file_path + ".enc", 'wb') as f:
        [f.write(x) for x in (salt, nonce, tag, ciphertext)]

def decrypt_file(file_path: str, password: str):
    with open(file_path, 'rb') as f:
        salt, nonce, tag, ciphertext = [f.read(x) for x in (16, 16, 16, -1)]

    key = PBKDF2(password, salt, dkLen=32)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

    data = cipher.decrypt_and_verify(ciphertext, tag)

    with open(file_path[:-4], 'wb') as f:
        f.write(data)
