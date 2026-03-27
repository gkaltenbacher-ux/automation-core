"""
Konfiguration — lädt Umgebungsvariablen aus .env
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

MASTER_KEY = os.getenv("MASTER_KEY")
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",")
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/database.db")
SESSION_TIMEOUT_HOURS = int(os.getenv("SESSION_TIMEOUT_HOURS", "24"))

# Pflicht-Variablen prüfen
_missing = []
if not MASTER_KEY:
    _missing.append("MASTER_KEY")
if not DASHBOARD_PASSWORD:
    _missing.append("DASHBOARD_PASSWORD")

if _missing:
    print(f"FEHLER: Folgende Umgebungsvariablen fehlen in .env: {', '.join(_missing)}")
    print("Kopiere .env.example nach .env und trage die Werte ein.")
    sys.exit(1)
