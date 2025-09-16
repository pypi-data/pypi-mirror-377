import os
import base64
from baza import SymmetricCrypto, AsymmetricCrypto, FileCrypto, hash_data, verify_hash
from baza.utils import write_file

# -------------------------
# Datos random en memoria
# -------------------------
random_bytes = os.urandom(32)
random_string = base64.b64encode(random_bytes).decode()
print("Random bytes:", random_bytes)
print("Random string:", random_string)

# -------------------------
# Encriptación de strings
# -------------------------
print("\n=== Encriptación de strings ===")
# Simétrica
sym_crypto = SymmetricCrypto()
enc_str = sym_crypto.encrypt(random_bytes)
dec_str = sym_crypto.decrypt(enc_str)
print("Simétrica encriptado:", enc_str)
print("Simétrica desencriptado:", dec_str)

# Asimétrica
asym_crypto = AsymmetricCrypto()
enc_str_rsa = asym_crypto.encrypt(random_bytes)
dec_str_rsa = asym_crypto.decrypt(enc_str_rsa)
print("Asimétrica encriptado:", enc_str_rsa)
print("Asimétrica desencriptado:", dec_str_rsa)

# -------------------------
# Hashing de strings
# -------------------------
print("\n=== Hashing ===")
for algo in ["argon2", "bcrypt", "sha256"]:
    h = hash_data(random_string, algo)
    print(f"{algo} hash:", h)
    print(f"{algo} verificada:", verify_hash(h, random_string, algo))

# -------------------------
# Encriptación de archivos
# -------------------------
print("\n=== Encriptación de archivos ===")
# Crear archivo de ejemplo
write_file("random_file.bin", random_bytes)

# Encriptar/Desencriptar simétrico
file_crypto = FileCrypto(algorithm="symmetric")
file_crypto.encrypt_file("random_file.bin", "random_file.enc")
file_crypto.decrypt_file("random_file.enc", "random_file_dec.bin")
print("Archivo simétrico encriptado y desencriptado.")

# Encriptar/Desencriptar asimétrico
file_crypto_rsa = FileCrypto(algorithm="asymmetric")
file_crypto_rsa.encrypt_file("random_file.bin", "random_file_rsa.enc")
file_crypto_rsa.decrypt_file("random_file_rsa.enc", "random_file_rsa_dec.bin")
print("Archivo asimétrico encriptado y desencriptado.")
