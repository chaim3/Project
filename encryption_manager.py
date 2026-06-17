# client/encryption_manager.py

ENCRYPT_PREFIX = "ENCRYPT|"  # prefix for encoded events


class EncryptionManager:
    def __init__(self, key: int = 0x3F):
        self.key = key  # XOR key for encryption/decryption

    def encrypt_bytes(self, data: bytes) -> bytes:
        return bytes([b ^ self.key for b in data])  # XOR each byte

    def decrypt_bytes(self, data: bytes) -> bytes:
        return self.encrypt_bytes(data)  # same XOR reverses itself

    def encrypt_text(self, text: str) -> str:
        raw = text.encode("utf-8")  # text to bytes
        enc = self.encrypt_bytes(raw)  # encrypt bytes
        return enc.hex().upper()  # hex string transport format

    def decrypt_text(self, hex_text: str) -> str:
        data = bytes.fromhex(hex_text)  # parse hex string
        dec = self.decrypt_bytes(data)  # decrypt bytes
        return dec.decode("utf-8", errors="ignore")  # bytes back to text


def encode_encrypted_event(event: str, enc_mgr: EncryptionManager) -> str:
    return f"{ENCRYPT_PREFIX}{enc_mgr.encrypt_text(event)}"  # prefix encrypted payload


def decode_encrypted_event(event: str, enc_mgr: EncryptionManager) -> str:
    if not event.startswith(ENCRYPT_PREFIX):
        raise ValueError("Expected encrypted event")  # validation check

    hex_data = event[len(ENCRYPT_PREFIX) :].split(" ", 1)[0]  # strip prefix
    if not hex_data:
        raise ValueError("Missing encrypted payload")
    return enc_mgr.decrypt_text(hex_data)  # decrypt and return text