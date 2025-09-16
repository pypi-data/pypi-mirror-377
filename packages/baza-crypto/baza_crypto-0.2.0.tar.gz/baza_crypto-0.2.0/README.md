# Baza

Baza es una librería de Python para **encriptación y hashing flexible**.

## Ejemplo de uso

```python
from baza import SymmetricCrypto, AsymmetricCrypto, hash_data, verify_hash

# --- Hashing ---
h = hash_data("mi_password", "argon2")
print("Hash:", h)
print("Verificada:", verify_hash(h, "mi_password", "argon2"))

# --- Encriptación simétrica ---
crypto = SymmetricCrypto()
token = crypto.encrypt(b"Hola mundo")
print("Encriptado:", token)
print("Desencriptado:", crypto.decrypt(token))

# --- Encriptación asimétrica ---
asym = AsymmetricCrypto()
enc = asym.encrypt(b"Mensaje secreto")
print("Encriptado:", enc)
print("Desencriptado:", asym.decrypt(enc))
