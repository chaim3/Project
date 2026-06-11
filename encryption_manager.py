# client/encryption_manager.py

class EncryptionManager:
    def __init__(self, key: int = 0x3F):
        self.key = key

    def encrypt_bytes(self, data: bytes) -> bytes:
        return bytes([b ^ self.key for b in data])

    def decrypt_bytes(self, data: bytes) -> bytes:
        return self.encrypt_bytes(data)

    def encrypt_text(self, text: str) -> str:
        raw = text.encode("utf-8")
        enc = self.encrypt_bytes(raw)
        return enc.hex().upper()

    def decrypt_text(self, hex_text: str) -> str:
        data = bytes.fromhex(hex_text)
        dec = self.decrypt_bytes(data)
        return dec.decode("utf-8", errors="ignore")