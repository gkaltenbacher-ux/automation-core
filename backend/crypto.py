"""
Verschlüsselung — Fernet (AES-128 + HMAC) für API-Keys.
MASTER_KEY aus .env wird als Fernet-Schlüssel verwendet.
"""

from cryptography.fernet import Fernet, InvalidToken
from backend.config import MASTER_KEY
from backend.database import db


fernet = Fernet(MASTER_KEY.encode())


def encrypt(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()


def decrypt(encrypted_value: str) -> str:
    return fernet.decrypt(encrypted_value.encode()).decode()


async def save_api_key(provider: str, key: str):
    """Verschlüsselt den Key und speichert ihn in der Datenbank."""
    encrypted = encrypt(key)
    await db.save_api_key(provider, encrypted)


def get_api_key(provider: str) -> str | None:
    """Holt den Key aus der DB und entschlüsselt ihn."""
    encrypted = db.get_api_key(provider)
    if encrypted is None:
        return None
    try:
        return decrypt(encrypted)
    except InvalidToken:
        return None


def get_masked_keys() -> list:
    """Gibt alle Keys maskiert zurück, z.B. sk-●●●●●●abc"""
    all_keys = db.get_all_api_keys()
    masked = []
    for row in all_keys:
        try:
            decrypted = decrypt(row["encrypted_key"])
            if len(decrypted) > 3:
                mask = decrypted[:3] + "●●●●●●" + decrypted[-3:]
            else:
                mask = "●●●●●●"
        except InvalidToken:
            mask = "●●●●●● (ungültig)"
        masked.append({
            "provider": row["provider"],
            "masked_key": mask,
            "updated_at": row["updated_at"],
        })
    return masked
