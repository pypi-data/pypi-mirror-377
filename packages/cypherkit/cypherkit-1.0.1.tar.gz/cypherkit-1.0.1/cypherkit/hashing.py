import hashlib

def generate_hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

def verify_hash(data: str, hash_value: str) -> bool:
    return generate_hash(data) == hash_value
