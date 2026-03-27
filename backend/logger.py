"""
Logger — schreibt über die Write-Queue in die Datenbank und auf die Konsole.
Log-Nachrichten in normaler Sprache, nicht technisch.
"""

from datetime import datetime
from backend.database import db


async def log(message: str, level: str = "info", automation_name: str = None):
    """Loggt eine Nachricht in die DB (via Write-Queue) und auf die Konsole."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = f"[{timestamp}] [{level.upper()}]"
    if automation_name:
        prefix += f" [{automation_name}]"
    print(f"{prefix} {message}")
    await db.save_log(message, level, automation_name)
