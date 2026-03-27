"""
Rate-Limiter — max 5 Login-Versuche pro IP pro Minute.
Nach 5 Fehlversuchen: 60 Sekunden Sperre.
"""

from backend.database import db


def check_rate_limit(ip_address: str) -> bool:
    """Prüft ob die IP noch Login-Versuche machen darf. True = erlaubt."""
    attempts = db.get_recent_login_attempts(ip_address, minutes=1)
    failed = [a for a in attempts if not a["success"]]
    return len(failed) < 5


async def record_attempt(ip_address: str, success: bool):
    """Speichert einen Login-Versuch."""
    await db.record_login_attempt(ip_address, success)
