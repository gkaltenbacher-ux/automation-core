# CLAUDE.md — Projekt-Regeln

## Projekt
Automations-Plattform für Consulting-Kunden.
Drei-Schichten-Architektur: Core (alle gleich) → Blocks (wiederverwendbar) → Config (kunden-spezifisch).

## Stack (NUR diese — KEINE anderen)
- Backend: FastAPI (Python 3.11+). NICHT Flask. NICHT Django. NICHT Express.
- Datenbank: SQLite mit Write-Queue. NICHT PostgreSQL. NICHT MongoDB. NICHT Redis.
- Dashboard: EINE HTML-Datei, Tailwind + Alpine.js via CDN. NICHT React. NICHT Vue. NICHT Svelte. NICHT Next.js. KEIN Build-Step. KEIN npm. Auch nicht "später". Auch nicht "nur für diesen Tab".
- Scheduling: APScheduler. NICHT Celery.
- Verschlüsselung: Fernet (cryptography). NICHT eigene Crypto.
- Container: Docker Compose. NICHT Kubernetes.

## Architektur-Regeln

### Regel 1: Drei Schichten respektieren
- core/ = Backend-Infrastruktur (ALLE Kunden gleich)
- blocks/ = Wiederverwendbare Automations-Bausteine (ALLE Kunden gleich)
- config/ = Kunden-spezifisch (NIE automatisch überschreiben)
- NIEMALS kunden-spezifische Logik in core/ oder blocks/

### Regel 2: Block-Interface (JEDER Block so)
async def execute(input_data: dict, config: dict, context: dict) -> dict
- input_data: Ausgabe des vorherigen Blocks
- config: Block-Einstellungen aus client.json
- context: {"log": log_fn, "get_api_key": fn, "db": db}
- return: {"success": True/False, "data": {...}, "error": "..."}

### Regel 3: Pipeline
- Automationen werden in client.json definiert, NICHT als Python-Code
- pipeline.py liest client.json, importiert Blocks, führt sie der Reihe nach aus
- Ausgabe Block N = Eingabe Block N+1

### Regel 4: Logging (mit Write-Queue)
- JEDER Schritt wird geloggt mit context["log"]()
- NORMALE SPRACHE: "3 neue E-Mails gefunden"
- NICHT: "Processed 3 items from IMAP queue"
- Writes gehen in asyncio.Queue, nicht direkt in SQLite

### Regel 5: API-Keys
- IMMER über context["get_api_key"]("provider")
- NIEMALS hardcoden
- .env nur für SYSTEM-Variablen

### Regel 6: Dashboard
- EINE index.html. KEIN Framework. KEIN Build-Step.
- Jeder Tab = eigenständiger Alpine.js x-data Block
- Dashboard liest api_keys_needed und automations aus client.json
- Texte auf Deutsch

### Regel 7: Sicherheit
- Fernet-Verschlüsselung für API-Keys
- Rate-Limiting: 5 Login-Versuche/Min/IP
- HTTPS-Redirect in Produktion
- /api/health OHNE Auth

### Regel 8: Docker
- docker compose up startet alles
- SQLite in /data/ (Volume)
- Dashboard wird als Static File serviert
