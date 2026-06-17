# client/encryption_manager.py

ENCRYPT_PREFIX = "ENCRYPT|"
VALID_TRANSPORT_PREFIXES = ("SPEED+", "SPEED-", "FOOD+", ENCRYPT_PREFIX)


def is_valid_transport_event(event: str) -> bool:
    return any(event.startswith(prefix) for prefix in VALID_TRANSPORT_PREFIXES)


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


def encode_encrypted_event(event: str, enc_mgr: EncryptionManager) -> str:
    return f"{ENCRYPT_PREFIX}{enc_mgr.encrypt_text(event)}"


def decode_encrypted_event(event: str, enc_mgr: EncryptionManager) -> str:
    if not event.startswith(ENCRYPT_PREFIX):
        return event

    hex_data = event[len(ENCRYPT_PREFIX) :].split(" ", 1)[0]
    return enc_mgr.decrypt_text(hex_data)