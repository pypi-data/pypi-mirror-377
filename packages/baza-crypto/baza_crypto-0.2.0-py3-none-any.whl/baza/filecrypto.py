from .symmetric import SymmetricCrypto
from .asymmetric import AsymmetricCrypto
from .hashing import hash_data, verify_hash
from .utils import read_file, write_file

class FileCrypto:
    """Clase para encriptar y desencriptar archivos completos"""

    def __init__(self, algorithm="symmetric"):
        """
        algorithm: "symmetric" | "asymmetric"
        """
        self.algorithm = algorithm
        if algorithm == "symmetric":
            self.crypto = SymmetricCrypto()
        elif algorithm == "asymmetric":
            self.crypto = AsymmetricCrypto()
        else:
            raise ValueError("Algoritmo no soportado")

    def encrypt_file(self, input_path: str, output_path: str):
        data = read_file(input_path)
        encrypted = self.crypto.encrypt(data)
        write_file(output_path, encrypted)

    def decrypt_file(self, input_path: str, output_path: str):
        data = read_file(input_path)
        decrypted = self.crypto.decrypt(data)
        write_file(output_path, decrypted)
