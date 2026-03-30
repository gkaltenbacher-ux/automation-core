# AgentCore24 — Plan: Agent-System Komplett

## Stand: 30. März 2026 (Analyse abgeschlossen)

---

## WAS WIR BAUEN

Ein System wo der Orchestrator-Agent als Zentrale arbeitet. Er bekommt einen Befehl (von dir via Telegram, Dashboard, oder automatisch via Cron) und entscheidet welchen Sub-Agent er braucht. Der Sub-Agent hat seine eigenen Tools, macht seine Arbeit, gibt das Ergebnis zurück. Der Orchestrator entscheidet dann ob er fertig ist oder einen weiteren Sub-Agent braucht.

**Kein Hin-und-Her zwischen Agents** — nur Orchestrator → Agent → Ergebnis → Orchestrator.

---

## DIE 5 BAUSTEINE

### 1. WORKFLOW-ENGINE (das Herzstück)

**Was:** Eine State-Machine die Workflows ausführt (wie LangGraph, aber ohne LangGraph).

**Warum:** Wenn du sagst "Scrape Leads und schick E-Mails", muss das System wissen: erst scrapen, dann scoren, dann CRM, dann E-Mail generieren, dann senden. Das ist ein Workflow mit definierten Schritten.

**So funktioniert es:**
```
Workflow = Abfolge von Schritten mit Bedingungen

Schritt 1: lead_researcher → Leads finden
  ↓ (wenn Leads gefunden)
Schritt 2: lead_researcher → Leads bewerten
  ↓ (wenn qualifizierte Leads > 0)
Schritt 3: outreach_agent → E-Mails generieren
  ↓ (zeige Ergebnis, warte auf Bestätigung)
Schritt 4: outreach_agent → E-Mails senden
  ↓
Schritt 5: crm_agent → Status im CRM updaten
```

**State:** Jeder Workflow hat einen State (wie ein Notizblock):
```json
{
  "workflow_id": "wf_20260330_001",
  "status": "running",
  "current_step": 2,
  "data": {
    "scraped_leads": [...],
    "scored_leads": [...],
    "generated_emails": [...],
    "sent_count": 0
  },
  "checkpoints": [...]
}
```

Wenn ein Schritt fehlschlägt → State wird gespeichert → Workflow kann ab dem letzten Checkpoint weitermachen.

**Dashboard-konfigurierbar:**
- Workflow-Schritte ein/ausschalten
- Bedingungen ändern (z.B. Threshold von 60 auf 80)
- Manuell starten / pausieren / fortsetzen
- Letzte Runs mit Status anschauen

---

### 2. ORCHESTRATOR (der Chef)

**Was:** Der zentrale Agent der entscheidet was passiert.

**So entscheidet er wen er ruft:**
- Er bekommt deinen Befehl als Text
- OpenAI Function Calling sagt ihm welcher Sub-Agent passt
- Jeder Sub-Agent ist als "Function" definiert mit klarer Beschreibung
- Das LLM matched deinen Befehl zum passenden Agent

**Beispiel:**
```
Du: "Finde 20 Marketing-Agenturen in Zürich"
→ Orchestrator erkennt: Lead-Suche → ruft lead_researcher
→ lead_researcher nutzt: scrape_google_maps + extract_emails + score_leads
→ Ergebnis: 20 Leads, 12 qualifiziert
→ Orchestrator zeigt dir: "12 qualifizierte Leads gefunden. Soll ich E-Mails generieren?"
```

**Was der Orchestrator NICHT macht:**
- Selber scrapen oder E-Mails schreiben (das machen Sub-Agents)
- Direkt mit APIs reden (das machen Tools)
- Ohne Bestätigung E-Mails senden

**Dashboard-konfigurierbar:**
- Welches LLM-Modell er nutzt (gpt-4o-mini für Budget, gpt-4o für Qualität)
- System-Prompt anpassen
- Welche Sub-Agents er kennt (ein/ausschaltbar)

---

### 3. SUB-AGENTS (die Spezialisten)

**Was:** Jeder Agent hat EINE klare Aufgabe und bekommt spezifische Tools zugewiesen.

**Aktuell geplante Agents:**

| Agent | Aufgabe | Tools |
|---|---|---|
| `lead_researcher` | Leads finden + qualifizieren | scrape_google_maps, scrape_linkedin, extract_emails, score_leads, generate_lead_id |
| `outreach_agent` | E-Mails generieren + senden | generate_text, send_gmail |
| `crm_agent` | CRM-Daten verwalten | sync_notion, check_duplicate |
| `analytics_agent` | Statistiken + Reports | query_crm_stats, calculate_conversion |

**So weiss ein Agent was er tun soll:**
1. Er hat einen System-Prompt der seine Rolle beschreibt
2. Er hat eine Liste von Tools die er nutzen darf
3. Er bekommt Input-Daten vom Orchestrator
4. Er nutzt OpenAI Function Calling um seine Tools aufzurufen
5. Er gibt ein strukturiertes Ergebnis zurück

**Wichtig:** Ein Agent in Projekt A kann ANDERE Tools haben als derselbe Agent in Projekt B. Die Zuordnung steht in `client.json`:

```json
{
  "agents": {
    "lead_researcher": {
      "tools": ["scrape_google_maps", "extract_emails", "score_leads"],
      "model": "gpt-4o-mini",
      "system_prompt": "Du bist ein Lead-Researcher..."
    }
  }
}
```

**Dashboard-konfigurierbar:**
- System-Prompt pro Agent
- Tool-Zuordnung (Checkboxen: welche Tools hat dieser Agent?)
- Modell-Auswahl pro Agent
- Agent ein/ausschalten

---

### 4. TOOLS (die Werkzeuge)

**Was:** Einfache Funktionen die EINE Sache tun. Agents rufen sie auf.

**Aktuell geplante Tools (Migration aus blocks/):**

| Tool | Was es macht | Braucht |
|---|---|---|
| `scrape_google_maps` | Google Maps via Apify | Apify Token |
| `scrape_linkedin` | LinkedIn via Apify | Apify Token |
| `extract_emails` | E-Mails von Websites | Apify Token |
| `score_leads` | Leads bewerten (0-100) | — |
| `generate_lead_id` | Eindeutige ID vergeben | Notion (für Duplikat-Check) |
| `generate_text` | Text via LLM generieren | OpenAI Key |
| `send_gmail` | E-Mail versenden | Gmail Credentials |
| `sync_notion` | CRM lesen/schreiben | Notion Token |
| `check_duplicate` | Duplikat prüfen | Notion Token |

**Tool-Interface (einfach):**
```python
async def run(params: dict, context: dict) -> dict:
    # params: Was das Tool braucht (z.B. query, max_results)
    # context: API-Keys, Logging, DB
    # return: {"success": True, "data": {...}}
```

**Dashboard-konfigurierbar:**
- Tool-Parameter (z.B. Apify Actor-IDs, Scoring-Regeln)
- API-Keys die das Tool braucht (über Credentials)

---

### 5. KOSTEN-TRACKING

**Was:** Jeder LLM-Call wird getrackt — Tokens, Kosten, welcher Agent, welcher Workflow.

**Warum:** Du musst wissen was ein Workflow kostet, um Kunden korrekt abzurechnen.

**So funktioniert es:**
- Jeder OpenAI-Call geht durch einen Wrapper der Tokens zählt
- Preise pro Modell sind hinterlegt (gpt-4o-mini: $0.15/1M input, gpt-4o: $2.50/1M input)
- Wird pro Agent, pro Workflow-Run, pro Tag gespeichert

**Dashboard-konfigurierbar:**
- Kosten-Übersicht pro Tag/Woche/Monat
- Kosten pro Agent
- Kosten pro Workflow-Run
- Budget-Limits (Warnung wenn Tageslimit erreicht)

---

## VERZEICHNIS-STRUKTUR (finale Version)

```
kunde-projekt/
├── core/                          ← Backend (alle Projekte gleich)
│   ├── backend/
│   │   ├── main.py               ← FastAPI + alle Endpoints
│   │   ├── orchestrator.py       ← Orchestrator-Agent (NEU)
│   │   ├── workflow_engine.py    ← State-Machine für Workflows (NEU)
│   │   ├── cost_tracker.py       ← Token/Kosten-Tracking (NEU)
│   │   ├── credentials.py        ← Credential-Manager
│   │   ├── telegram_bot.py       ← Telegram-Integration
│   │   ├── database.py           ← SQLite
│   │   ├── scheduler.py          ← Cron-Jobs
│   │   ├── config.py             ← Environment
│   │   ├── crypto.py             ← Verschlüsselung
│   │   ├── logger.py             ← Logging
│   │   └── rate_limiter.py       ← Rate-Limiting
│   └── dashboard/
│       └── index.html            ← Dashboard (Basis + Projekt-Tabs)
│
├── agents/                        ← Sub-Agents (pro Projekt konfigurierbar)
│   ├── __init__.py               ← Agent-Registry
│   ├── base_agent.py             ← Basis-Klasse
│   ├── lead_researcher.py        ← Lead-Agent
│   ├── outreach_agent.py         ← E-Mail-Agent
│   └── crm_agent.py              ← CRM-Agent
│
├── tools/                         ← Tools die Agents nutzen
│   ├── __init__.py               ← Tool-Registry
│   ├── scrape_google_maps.py
│   ├── scrape_linkedin.py
│   ├── extract_emails.py
│   ├── score_leads.py
│   ├── generate_lead_id.py
│   ├── generate_text.py
│   ├── send_gmail.py
│   ├── sync_notion.py
│   └── check_duplicate.py
│
├── blocks/                        ← Legacy (wird schrittweise nach tools/ migriert)
│
├── config/
│   ├── client.json               ← Agents, Tools, Workflows, Schedules
│   └── custom_prompts/           ← Prompt-Templates
│
├── Dockerfile
└── docker-compose.yml
```

---

## DASHBOARD-PLAN

### Basis-Tabs (jedes Projekt)

| Tab | Was | Konfigurierbar |
|---|---|---|
| **Credentials** | API-Keys, Tokens, Webhooks | Hinzufügen, Testen, Löschen |
| **Agents** | Sub-Agents verwalten | System-Prompt, Tools, Modell, An/Aus |
| **Workflows** | Automatisierungen | Schritte, Bedingungen, Cron, An/Aus |
| **Kosten** | Token-Verbrauch + Kosten | Budget-Limits, Zeitraum |
| **Logs** | Live-Aktivität | Filter nach Agent/Workflow/Level |

### Projekt-spezifische Tabs (je nach Kunde)

Für Lead-System:
- Lead-Scraping Konfigurator (Apify-Einstellungen)
- Prompt-Editor (E-Mail-Templates)
- Webhooks (Cal.com, Tally)

Für anderen Kunden:
- Komplett andere Tabs

---

## REIHENFOLGE DER UMSETZUNG

```
TAG 1: Tools migrieren
  □ blocks/ → tools/ (9 Tools)
  □ Tool-Registry testen
  □ Alte Blocks als Wrapper behalten (Kompatibilität)

TAG 2: Sub-Agents bauen
  □ lead_researcher.py (nutzt 5 Tools)
  □ outreach_agent.py (nutzt 3 Tools)
  □ crm_agent.py (nutzt 2 Tools)
  □ Agent ↔ Tool Zuordnung in client.json

TAG 3: Workflow-Engine
  □ workflow_engine.py (State-Machine)
  □ State-Management (Checkpoints, Resume)
  □ Bestehende Automationen als Workflows definieren
  □ Cron-Trigger verbinden

TAG 4: Orchestrator neu
  □ orchestrator.py neu (Sub-Agents statt Tools direkt)
  □ Routing-Logik (welcher Agent für welchen Befehl)
  □ Telegram-Integration updaten
  □ Dashboard-Integration

TAG 5: Dashboard erweitern
  □ Agents-Tab (Prompts, Tools, Modell editieren)
  □ Workflows-Tab (Schritte, Status, Trigger)
  □ Kosten-Tab
  □ Dashboard-Basis als Template extrahieren

TAG 6: Kosten-Tracking + Polish
  □ cost_tracker.py
  □ Token-Zählung pro Agent/Workflow
  □ Budget-Limits
  □ Testen, fixen, deployen
```

---

## WAS MORGEN ZUERST

**Tag 1: Tools migrieren.** Das ist die Grundlage — ohne Tools können Agents nichts tun.

Sage: "Weiter mit Tag 1" und wir starten.
