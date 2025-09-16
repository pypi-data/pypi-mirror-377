import hashlib
from argon2 import PasswordHasher
import bcrypt

ph = PasswordHasher()

def hash_data(data: str, algorithm="argon2") -> str:
    if algorithm == "argon2":
        return ph.hash(data)
    elif algorithm == "bcrypt":
        return bcrypt.hashpw(data.encode(), bcrypt.gensalt()).decode()
    elif algorithm == "sha256":
        return hashlib.sha256(data.encode()).hexdigest()
    else:
        raise ValueError("Algoritmo no soportado")

def verify_hash(hash_value: str, data: str, algorithm="argon2") -> bool:
    if algorithm == "argon2":
        try:
            ph.verify(hash_value, data)
            return True
        except:
            return False
    elif algorithm == "bcrypt":
        return bcrypt.checkpw(data.encode(), hash_value.encode())
    elif algorithm == "sha256":
        return hashlib.sha256(data.encode()).hexdigest() == hash_value
    else:
        raise ValueError("Algoritmo no soportado")
