from cryptography.fernet import Fernet

class SymmetricCrypto:
    def __init__(self, key=None):
        """Si no se pasa clave, se genera una nueva"""
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def encrypt(self, data: bytes) -> bytes:
        """Encripta bytes"""
        return self.cipher.encrypt(data)

    def decrypt(self, token: bytes) -> bytes:
        """Desencripta bytes"""
        return self.cipher.decrypt(token)
