# AGENTCORE24 — Das komplette System in einer Datei
# Version 8.0 — Ein-Gehirn-System mit Sub-Agents
# Stand: März 2026

---

# TEIL A: FÜR CLAUDE CODE

## Über Grischa

- Grischa ist KEIN Entwickler. Er kann keinen Code lesen oder schreiben.
- Erkläre jeden Schritt so dass ein Nicht-Techniker ihn versteht.
- Mache technische Schritte selbst, frage nicht ob er sie manuell machen will.
- Grischa arbeitet mit Warp als Terminal.
- Deutsch, informell. Wenn er sagt "mach das" — mach es, frage nicht dreimal.
- Lies IMMER zuerst `system_memory.json` für aktuelle Infos.

## Arbeitsablauf: NUR Claude Code

Es gibt keinen separaten Planer mehr. Claude Code macht ALLES:

```
GRISCHA → Claude Code → Plant → Fragt nach → Baut → Testet → Deployt → Lernt
```

### Planmodus (wenn Grischa "Neuer Kunde" oder ein neues Feature beschreibt)

1. **Zuhören** — Grischa beschreibt was er/der Kunde will
2. **Rückfragen stellen** — ALLE relevanten Fragen auf einmal:
   - Was genau soll automatisiert werden?
   - Welche Tools/APIs nutzt der Kunde schon?
   - Welche Daten müssen wohin fliessen?
   - Was sind die Trigger (Zeit, Event, manuell)?
   - Welche Agents/Tools existieren schon die wiederverwendbar sind?
   - Budget/Prioritäten?
3. **Recherchieren** — Vor dem Bauen:
   - Welche APIs gibt es? Was kosten sie?
   - Welche Blocks/Tools/Agents existieren schon?
   - Was ist der effizienteste/günstigste Weg?
   - Sicherheits-Aspekte?
4. **Plan präsentieren** — Architektur, Agents, Tools, Kosten
5. **Grischa sagt "Go"** — Erst dann bauen
6. **Bauen** — Schritt für Schritt, mit Tests nach jedem Schritt
7. **Deployen** — Docker, Coolify, Domain
8. **System-Memory aktualisieren** — Learnings, neue Blocks, neue Patterns

### Regeln für Claude Code

- Erkläre jeden Schritt bevor du ihn ausführst
- Teste nach jedem Build-Schritt
- Nie mehr als einen Schritt ohne Bestätigung
- Log-Nachrichten und Dashboard-Texte auf Deutsch
- Nutze IMMER bestehende Tools/Agents wenn möglich
- Neuer Code → blocks_library.json + agents_library.json updaten
- Nach jedem Projekt → system_memory.json updaten + git push

---

# TEIL B: DAS PROJEKT

## In einem Satz

Grischa baut mit Claude Code Agent-Systeme für Kunden. Jeder Kunde bekommt ein Dashboard + Sub-Agents die seine Arbeitsprozesse automatisieren. Das System lernt mit jedem Projekt dazu.

## Kern-Prinzipien

**1. Ein Gehirn** — Claude Code plant UND baut. Kein separater Planer.

**2. Vier Schichten** — Core (alle Kunden gleich) → Agents (wiederverwendbar) → Tools (wiederverwendbar) → Config (kunden-spezifisch).

**3. Agents + Tools statt Pipelines** — Orchestrator-Agent steuert Sub-Agents. Sub-Agents nutzen Tools. Flexibler als starre Block-Ketten.

**4. Konfiguration statt Code** — client.json steuert alles. Welche Agents aktiv sind, welche Tools sie nutzen, wann sie laufen.

**5. Dashboard = Basis + Flexibel** — Jedes Projekt hat das gleiche Dashboard-Framework (Login, Tabs, Credentials, Logs) aber projekt-spezifische Tabs werden hinzugefügt.

**6. BYOK** — Kunde zahlt seine API-Kosten selbst.

**7. Das System lernt** — system_memory.json wird automatisch aktualisiert. Jedes Projekt macht das System besser.

---

# TEIL C: ARCHITEKTUR

## Vier Code-Schichten

```
automation-core/ (GitHub Repo)
├── AGENTCORE24.md              ← Dieses Dokument
├── system_memory.json          ← Das lernende Gedächtnis
├── CLAUDE.md                   ← Regeln für Claude Code
└── core/                       ← Backend-Code (FastAPI, DB, Scheduler, Dashboard-Basis)

automation-blocks/ (GitHub Repo)
├── blocks_library.json         ← Block-Katalog (Legacy + neue Tools)
├── agents_library.json         ← Agent/Pattern-Katalog
└── blocks/                     ← Block-Code (Legacy-Interface)

Kunden-Projekte (je ein Repo)
├── core/                       ← Git Subtree aus automation-core
├── blocks/                     ← Git Subtree aus automation-blocks
├── agents/                     ← SUB-AGENTS (pro Projekt konfigurierbar)
│   ├── __init__.py             ← Agent-Registry
│   ├── base_agent.py           ← Basis-Klasse
│   ├── lead_researcher.py      ← Beispiel: Lead-Agent
│   └── outreach_agent.py       ← Beispiel: Outreach-Agent
├── tools/                      ← TOOLS (wiederverwendbar, Agents nutzen sie)
│   ├── __init__.py             ← Tool-Registry
│   ├── scrape_google_maps.py   ← Beispiel
│   └── send_gmail.py           ← Beispiel
├── config/
│   ├── client.json             ← Steuert Agents, Tools, Automationen
│   └── custom_prompts/         ← Kunden-Prompts
├── CLAUDE.md                   ← Projekt-Regeln
├── Dockerfile
└── docker-compose.yml
```

## Agent-Architektur

```
┌──────────────────────────────────────────────────┐
│  ORCHESTRATOR (core/backend/orchestrator.py)     │
│  Empfängt Befehle via:                           │
│  ├── Telegram Bot                                │
│  ├── Dashboard API                               │
│  ├── Scheduled Automationen                      │
│  └── Webhooks (Cal.com, Tally, etc.)             │
│                                                  │
│  Entscheidet: Welcher Sub-Agent? Welche Tools?   │
└────────────────┬─────────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ Agent A │ │ Agent B │ │ Agent C │
│         │ │         │ │         │
│ Tools:  │ │ Tools:  │ │ Tools:  │
│ - T1    │ │ - T2    │ │ - T1    │  ← Agents können
│ - T3    │ │ - T4    │ │ - T5    │    gleiche Tools teilen
└─────────┘ └─────────┘ └─────────┘
```

Wichtig:
- Sub-Agents reden NICHT miteinander (Token sparen)
- Orchestrator → Sub-Agent → Ergebnis → Orchestrator
- Ein Sub-Agent kann in verschiedenen Projekten verschiedene Tools bekommen

## Dashboard-Architektur (Basis + Flexibel)

```
DASHBOARD BASIS (jedes Projekt gleich):
├── Login (Passwort, Rate-Limiting)
├── Tab: Credentials (API-Keys, Bot-Tokens, Webhooks)
├── Tab: Automationen (Status, Toggle, Manual Trigger)
├── Tab: Aktivität/Logs (Live-Stream, Filter)
└── Tab-Framework (neue Tabs einfach hinzufügbar)

DASHBOARD PROJEKT-SPEZIFISCH (je nach Kunde):
├── Tab: Lead-Scraping Konfigurator (Lead-System)
├── Tab: Prompt-Editor (Lead-System)
├── Tab: Webhook-Config (Lead-System)
├── Tab: [Kunde X spezifisch] (anderes Projekt)
└── Tab: [Kunde Y spezifisch] (anderes Projekt)
```

---

# TEIL D: FORTSCHRITTS-TRACKER

```
PHASE 1-7: GRUNDSYSTEM                   ✅ KOMPLETT
─────────────────────────────────────────────────
Server: 178.104.122.219 | Live: https://agentcore24.com | v0.1

PHASE 8: PLANUNGS-SYSTEM                  ✅ KOMPLETT
─────────────────────────────────────────────────
Repos öffentlich, Raw-URLs, Planer liest Dateien live.

PHASE 9A: EIGENER TEST (Lead-System)      ✅ KOMPLETT
─────────────────────────────────────────────────
✅ 9A.1  Produkt-Repo (kunde-grischa-leadsystem)
✅ 9A.2  client.json (10 Blocks, 3 Automationen, 2 Webhooks)
✅ 9A.3  9 neue Blocks + 5 Prompt-Templates
✅ 9A.4  Dashboard (6 Tabs, 25+ API-Endpoints)
✅ 9A.5  Deployed (leadsystem.agentcore24.com)
✅ 9A.6  Telegram Bot + Credential System + Orchestrator
✅ 9A.7  Apify Scraper mit korrekten Actor-IDs + Dashboard-Konfigurator

PHASE 9B: SYSTEM-UMBAU                   ← AKTUELL
─────────────────────────────────────────────────
✅ 9B.1  AGENTCORE24.md umgeschrieben (Ein-Gehirn-System)
✅ 9B.2  agents/ + tools/ Verzeichnisse erstellt
✅ 9B.3  BaseAgent + Tool-Registry
□ 9B.4  system_memory.json umstrukturieren
□ 9B.5  CLAUDE.md Template für Agent-Projekte

PHASE 9C: AGENT-FRAMEWORK                Status
─────────────────────────────────────────────────
□ 9C.1  Orchestrator-Agent neu (zentrale Steuerung)
□ 9C.2  Bestehende Blocks → Tools migrieren
□ 9C.3  Erste Sub-Agents bauen (Lead-Researcher, Outreach)
□ 9C.4  Agent ↔ Tool Zuordnung via client.json
□ 9C.5  Lern-System (Agents verbessern sich)

PHASE 9D: CLAUDE CODE WORKFLOW            Status
─────────────────────────────────────────────────
□ 9D.1  "Neuer Kunde" Workflow testen
□ 9D.2  Recherche-Phase einbauen
□ 9D.3  Automatische Stack-Erweiterung
□ 9D.4  Dashboard-Basis als wiederverwendbares Template
□ 9D.5  v0.2 taggen

PHASE 10: ERSTES KUNDEN-PRODUKT          Status
─────────────────────────────────────────────────
□ 10.1 Kunden-Repo mit Agent-Architektur
□ 10.2 Agents + Tools für Kundenfall
□ 10.3 Dashboard (Basis + Kunden-Tabs)
□ 10.4 Getestet + deployed
□ 10.5 System-Memory aktualisiert

PHASE 11: STABILISIERUNG                  Status
─────────────────────────────────────────────────
□ 11.1 Kunden-Feedback einarbeiten
□ 11.2 Kosten-Tracking Modul
□ 11.3 Update-Skript (update_all.sh)
□ 11.4 Kunden-Anleitung + Checklisten
□ 11.5 v1.0 getaggt
```

---

# TEIL E: KUNDEN-ABLAUF (Neu: Nur Claude Code)

```
A: ERSTGESPRÄCH  → Call mit Kunde, Transkript erstellen
B: PLANEN        → Claude Code: Rückfragen → Plan → "Go"
C: RECHERCHE     → Claude Code: APIs, Kosten, bestehende Tools prüfen
D: BAUEN         → Claude Code: Agents + Tools + Dashboard + Tests
E: DEPLOYEN      → Claude Code: Docker, Coolify, Domain, SSL
F: ÜBERGABE      → Screen-Share, Kunde trägt Keys ein
G: BETRIEB       → Monitoring, Telegram-Bot für Steuerung
H: LERNEN        → system_memory.json automatisch aktualisiert
```

## Phase B im Detail (Planmodus in Claude Code)

Grischa sagt: "Neuer Kunde: [Name], [Branche], [Infos aus Call]"

Claude Code:
1. Liest system_memory.json (ähnliche Projekte? Bewährte Patterns?)
2. Stellt ALLE Rückfragen auf einmal:
   - Welche Prozesse sollen automatisiert werden?
   - Welche Tools/Software nutzt der Kunde?
   - Welche Datenquellen gibt es?
   - Was sind die Trigger (Zeit? Event? Manuell?)
   - Budget-Rahmen?
   - Gibt es besondere Anforderungen (Sicherheit, Datenschutz)?
3. Grischa antwortet
4. Claude Code erstellt Plan:
   - Welche Agents werden gebraucht?
   - Welche Tools pro Agent?
   - Welche bestehenden Tools können wiederverwendet werden?
   - Was muss neu gebaut werden?
   - Geschätzte Kosten (API + Setup)
   - Architektur-Diagramm
5. Grischa sagt "Go" → Claude Code baut

---

# TEIL F: STACK

## Technologie (NUR diese)

- Backend: FastAPI (Python 3.11+). NICHT Flask/Django.
- Datenbank: SQLite mit Write-Queue. NICHT PostgreSQL.
- Dashboard: EINE HTML-Datei, Tailwind + Alpine.js. KEIN React. KEIN npm.
- Scheduling: APScheduler. NICHT Celery.
- Verschlüsselung: Fernet. Container: Docker Compose.
- AI: OpenAI Function Calling. KEIN LangChain (zu schwer).
- Telegram: python-telegram-bot (Webhook-Modus).
- Scraping: Apify API (Actors als Service).
- CRM: Notion API.

## Kosten pro Kunde

| Posten | Monatlich |
|---|---|
| Hetzner CX22 + Snapshots | ~€4.55 |
| Coolify + SSL + UptimeRobot | €0 |
| **Gesamt Infrastruktur** | **~€5-6** |

## Pricing

| Leistung | Preis |
|---|---|
| Setup + Basis-Automationen | CHF 1'500-3'000 |
| Monatliche Betreuung | CHF 200-500/Monat |
| Erweiterungsmodul | CHF 500-2'000 |

---

# SESSION-LOG

- 2026-03-27 — Phase 1-7 komplett. Live auf https://agentcore24.com. v0.1 getaggt.
- 2026-03-28 — Phase 8 komplett. Repos öffentlich, Planer liest Dateien live.
- 2026-03-30 — Phase 9A komplett. Lead-System gebaut: 16 Blocks, 5 Patterns, 6 Dashboard-Tabs, Telegram Bot, Credential System. Live auf leadsystem.agentcore24.com.
- 2026-03-30 — Phase 9B gestartet. System-Umbau: Ein-Gehirn (nur Claude Code), agents/ + tools/ Verzeichnisse, BaseAgent-Klasse, AGENTCORE24.md v8.0.
