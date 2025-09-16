# CypherKit

A Python library that helps you secure your data - encrypt files, protect passwords, send secret messages, and hide text in images.

## Features

- **Password Management**: Hash passwords securely with PBKDF2, verify passwords, and generate random passwords
- **File Encryption**: Encrypt/decrypt files using AES-256-GCM with password-based key derivation
- **Message Encryption**: Encrypt text messages with AES-256-GCM encryption
- **Data Hashing**: Generate and verify SHA-256 hashes for data integrity
- **Steganography**: Hide secret messages inside images using LSB technique

## Installation

```bash
pip install cypherkit
```

## Quick Start

### Password Management
```python
from cypherkit import hash_password, verify_password, generate_password

# Hash a password
hashed = hash_password("my_password")
print(verify_password(hashed, "my_password"))  # True

# Generate random password
password = generate_password(16)
print(password)
```

### File Encryption
```python
from cypherkit import encrypt_file, decrypt_file

# Encrypt and decrypt files
encrypt_file('document.txt', 'password123')
decrypt_file('document.txt.enc', 'password123')
```

### Message Encryption
```python
from cypherkit import encrypt_message, decrypt_message
import os

key = os.urandom(32)  # 256-bit key
encrypted = encrypt_message("Secret message", key)
decrypted = decrypt_message(encrypted, key)
print(decrypted)
```

### Hide Messages in Images
```python
from cypherkit import encode_message, decode_message

# Hide message in image
encode_message('photo.png', 'Hidden message', 'output.png')

# Extract hidden message
message = decode_message('output.png')
print(message)
```

## Requirements

- Python 3.7+
- pycryptodome
- Pillow

## Security

- PBKDF2 password hashing with 100,000 iterations
- AES-256-GCM encryption for files and messages
- Cryptographically secure random generation
- Automatic salt generation for password protection

## License

MIT License

## Links

- **GitHub**: https://github.com/FahimDidnt/CypherKit
- **Documentation**: https://github.com/FahimDidnt/CypherKit#readme
- **Issues**: https://github.com/FahimDidnt/CypherKit/issues