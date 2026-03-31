# Update-Prozess — Zero-Downtime Kundensysteme optimieren

## Rollen

| Wer | Aufgabe |
|-----|---------|
| **Grischa** | Strategie. Bespricht mit Kunden. Sagt "Go" bei Optimierungen. |
| **Kunde** | Nutzt Dashboard. Traegt API-Keys ein. Waehlt Workflow-Zeiten. |
| **Claude Code** | Baut, testet, optimiert, deployed. Der Techniker. |

## Monatlicher Optimierungs-Zyklus

### 1. Analyse (automatisch)
- system_memory.json lesen → neue Learnings seit letztem Zyklus
- Pro Kundenprojekt: client.json vergleichen mit aktuellen Best Practices
- Delta identifizieren:
  - Veraltete Prompts? → neuere Version verfuegbar
  - Teures Model? → guenstigere Alternative gleicher Qualitaet
  - Veraltete API-Parameter? → neue Actor-Versionen
  - Neue Learnings anwendbar? → z.B. bessere Rate-Limits

### 2. Kategorisierung
**Sichere Aenderungen (automatisch anwendbar):**
- Prompt-Updates (Text aendern, kein neuer Code)
- Model-Wechsel (config aendern)
- Parameter-Optimierung (Timeouts, Batch-Sizes, Rate-Limits)
- Kosten-Optimierung (guenstigeres Model bei gleicher Qualitaet)

**Unsichere Aenderungen (nur mit Grischa besprechen):**
- Neue Tools/Agents hinzufuegen
- Workflow-Logik aendern
- API-Provider wechseln
- Neue Features

### 3. Testen (BEVOR Push)
```bash
# Import-Test: Alle Module ladbar?
python3 -c "from backend.main import app; print('OK')"

# Registry-Test: Tools + Agents gefunden?
python3 -c "from tools import load_tool_registry; from agents import load_agent_registry; ..."

# Server-Test: Startet ohne Fehler?
# Starte Server lokal, teste Endpoints:
curl /api/health
curl /api/agents
curl /api/workflows
curl /api/credentials/types
```

### 4. Deploy (Samstag Nacht EU-Zeit)
```bash
# 1. Git Tag setzen (Rollback moeglich)
git tag -a v$(date +%Y%m%d) -m "Pre-update backup"
git push --tags

# 2. Aenderungen committen + pushen
git add . && git commit -m "Monthly optimization: [was geaendert]"
git push

# 3. Coolify deployed automatisch
# Credentials bleiben erhalten (SQLite in /data/ Volume)
# Workflow-Status bleibt erhalten (DB in /data/)
```

### 5. Was passiert mit Kundendaten beim Deploy?
- **Credentials**: Gespeichert in `/data/credentials.db` → Docker Volume → BLEIBT
- **Workflow-Runs**: Gespeichert in `/data/workflows.db` → BLEIBT
- **Logs**: Gespeichert in `/data/database.db` → BLEIBT
- **Kosten**: Gespeichert in `/data/costs.db` → BLEIBT
- **Alles in /data/**: Persistent Volume, wird NIE geloescht bei Deploy

### 6. Zero-Downtime
- Coolify macht Rolling Deployment: neuer Container startet → Health-Check → alter Container stoppt
- Kunde merkt nichts (max 2-3 Sekunden Umschaltung)
- Immer Samstag Nacht (wenig Traffic)
- Bei Health-Check Fehler: alter Container laeuft weiter (kein Rollout)

## Was NICHT geaendert wird ohne Ruecksprache
- Workflow-Logik (Reihenfolge der Steps)
- Neue Agents/Tools (muessen erst besprochen werden)
- Credential-Typen (Kunde muesste neue Keys eintragen)
- Dashboard-Struktur
- Alles wo unklar ist ob es funktioniert

## system_memory.json Tracking
Nach jedem Optimierungs-Zyklus:
```json
{
  "optimization": {
    "customer_projects": {
      "kunde_xyz": {
        "last_optimized": "2026-04-26",
        "applied_learnings": [
          "prompt_v3_outreach",
          "model_switch_gpt4o_mini_scoring"
        ]
      }
    }
  }
}
```
