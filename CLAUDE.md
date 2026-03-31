# CLAUDE.md — Projekt-Regeln

## Was ist das
Automation-Plattform fuer Consulting-Kunden. Grischa baut mit Claude Code Agent-Systeme.
Blueprint waehlen → Config anpassen → deployen. Jedes Projekt wird einfacher.

## Ordnerstruktur
```
automation-core/
  backend/           ← FastAPI Server (ALLE Kunden gleich)
    main.py          ← Endpoints + App-Start
    credentials.py   ← API-Key Verwaltung (Fernet, config-getrieben)
    orchestrator.py  ← Chat-Routing zu Agents (OpenAI Function Calling)
    workflow_engine.py ← Sequenzielle Workflows mit Pause/Resume
    cost_tracker.py  ← Token + Kosten pro LLM-Call
    dsgvo.py         ← DSGVO Compliance (Consent, Export, Loeschung)
    telegram_bot.py  ← Telegram Integration (optional, config-getrieben)
    database.py      ← SQLite + Write-Queue
    pipeline.py      ← Legacy Block-Pipeline
    scheduler.py     ← APScheduler Cron-Jobs
    config.py        ← .env Variablen
    crypto.py        ← Legacy Verschluesselung (ersetzt durch credentials.py)
    logger.py        ← Logging
    rate_limiter.py  ← Login Rate-Limiting
  agents/            ← Sub-Agents (pro Projekt konfigurierbar)
    base_agent.py    ← Basis-Klasse (execute, use_tool, call_llm)
    __init__.py      ← Auto-Discovery Registry
  tools/             ← Wiederverwendbare Funktionen
    base_tool.py     ← Basis-Klasse
    generate_text.py ← Referenz-Tool (OpenAI)
    __init__.py      ← Auto-Discovery Registry
  config/            ← Kunden-spezifisch
    client.json      ← STEUERT ALLES (Agents, Tools, Workflows, Credentials)
    custom_prompts/  ← Prompt-Templates
  dashboard/
    index.html       ← EINE HTML-Datei, 7 Tabs (Tailwind + Alpine.js)
  blueprints/        ← Projekt-Vorlagen (Blueprint waehlen → Config kopieren)
    lead_generation/ ← Erster Blueprint (Lead-Scraping + Outreach)
  data/              ← Laufzeit-Daten (SQLite, Keys) — im Docker Volume
```

## Stack (NUR diese)
- Backend: FastAPI (Python 3.11+). NICHT Flask/Django.
- Datenbank: SQLite. NICHT PostgreSQL.
- Dashboard: EINE HTML-Datei, Tailwind + Alpine.js. NICHT React. KEIN npm.
- AI: OpenAI Function Calling. NICHT LangChain.
- Scheduling: APScheduler. NICHT Celery.
- Verschluesselung: Fernet. Container: Docker Compose.

## Architektur-Regeln

1. **Alles ueber client.json** — Agents, Tools, Workflows, Credentials, DSGVO. Kein Code aendern fuer neues Projekt.
2. **Tool-Interface:** `async def run(params, context) -> dict`
3. **Agent-Interface:** Erbt von BaseAgent, hat execute() + use_tool()
4. **Orchestrator:** Liest Agents aus Config, routet via Function Calling
5. **Logging:** Normale Sprache ("3 Leads gefunden"), kein Tech-Jargon
6. **API-Keys:** Immer via `context["get_api_key"]()`, nie hardcoden
7. **Dashboard:** EINE index.html, Alpine.js x-data pro Tab, Deutsch
8. **Sicherheit:** Fernet, Rate-Limiting, HTTPS-Redirect
9. **Docker:** `docker compose up` startet alles, SQLite in /data/
10. **DSGVO:** Consent-Logging, Daten-Export, Daten-Loeschung, Audit-Trail

## Neues Projekt
→ Siehe NEW_PROJECT.md
