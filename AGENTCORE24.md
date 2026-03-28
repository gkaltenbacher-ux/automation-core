# AGENTCORE24 — Das komplette System in einer Datei
# Version 7.0 — Selbstlernendes Zwei-Gehirne-System
# Stand: März 2026

---

# TEIL A: FÜR CLAUDE CODE UND PLANER

## Über Grischa

Lies IMMER zuerst `system_memory.json` für aktuelle Infos über Grischas Arbeitsweise.
Falls nicht erreichbar, gelten diese Grundregeln:

- Grischa ist KEIN Entwickler. Er kann keinen Code lesen oder schreiben.
- Erkläre jeden Schritt so dass ein Nicht-Techniker ihn versteht.
- Mache technische Schritte selbst, frage nicht ob er sie manuell machen will.
- Grischa arbeitet mit Warp als Terminal.
- Deutsch, informell. Wenn er sagt "mach das" — mach es, frage nicht dreimal.

## Rollen

- **Planer (Claude.ai Project):** Plant Automationen, erstellt Angebote und Baupläne, generiert Claude Code Prompts.
- **Umsetzer (Claude Code in Warp):** Baut, testet, deployt, aktualisiert System-Dateien.
- **Grischa:** Beschreibt was er will, prüft im Browser, gibt Feedback.

## Regeln für Claude Code

- Erkläre jeden Schritt bevor du ihn ausführst
- Teste nach jedem Build-Schritt automatisch
- Mache nie mehr als einen Schritt auf einmal ohne Bestätigung
- Schreibe Log-Nachrichten und Dashboard-Texte auf Deutsch
- Wenn Grischa fragt "wo stehen wir?" → Fortschritts-Tracker lesen

## Automatisches Lernen (nach JEDEM Schritt, ohne zu fragen)

### Was du AUTOMATISCH aktualisierst (kein Nachfragen):

**AGENTCORE24.md:**
- Fortschritts-Tracker: Schritt abhaken, Infos notieren
- SESSION-LOG: Was geschafft wurde

**system_memory.json:**
- `about_grischa.gelernt` → Muster in seiner Arbeitsweise die du erkennst
- `system_learnings.blocks` → Block-Probleme + wie gefixt
- `system_learnings.claude_code_regeln` → Neue Best-Practices
- `system_learnings.deployment` → Coolify/Docker Probleme + Lösungen
- `kunden_erfahrungen` → Setup-Dauer, Blocks, Patterns, Pricing
- `planer_optimierungen` → Was im Planungsprozess gut funktioniert hat

**blocks_library.json:** Bei neuem Block → neuer Eintrag + statistics updaten
**agents_library.json:** Bei neuem Pattern → neuer Eintrag

### EINE Frage an Grischa (nur nach Kunden-Projekten):

"Projekt fertig. Ich habe [X] Learnings automatisch gespeichert.
Kurze Frage: War der Kunde zufrieden und gibt es was das ich nicht sehen konnte?"

### git commit + push nach jedem Update.

---

# TEIL B: DAS PROJEKT

## In einem Satz

Grischa baut mit Claude Code Automations-Systeme für Kunden. Jeder Kunde bekommt ein Dashboard. Die Automationen werden aus wiederverwendbaren Bausteinen zusammengesteckt. Das System lernt mit jedem Projekt dazu.

## Kern-Prinzipien

**1. Zwei Gehirne, ein System** — Planer plant, Claude Code baut. Beide lesen system_memory.json. Was einer lernt, weiss der andere sofort.

**2. Drei Schichten** — Core (alle Kunden gleich) → Blocks (wiederverwendbar) → Config (kunden-spezifisch).

**3. Konfiguration statt Code** — client.json steuert alles. Neue Kunden = konfigurieren, nicht programmieren.

**4. Dashboard bleibt HTML** — Eine Datei, Tailwind + Alpine.js via CDN. Kein React. Nie.

**5. BYOK** — Kunde zahlt seine API-Kosten selbst.

**6. Das System lernt** — system_memory.json wird automatisch aktualisiert. Jedes Projekt macht das System besser.

---

# TEIL C: FORTSCHRITTS-TRACKER

```
PHASE 1-7: GRUNDSYSTEM                   ✅ KOMPLETT
─────────────────────────────────────────────────
Server: 178.104.122.219 | Live: https://agentcore24.com | v0.1

PHASE 8: PLANUNGS-SYSTEM (vorher 11)      ← AKTUELL
─────────────────────────────────────────────────
✅ 8.1  system_memory.json ins Core-Repo    [x]
□ 8.2  GitHub Pages aktivieren (beide Repos)[ ]
✅ 8.3  Claude.ai Project "Planer" erstellt [x]
✅ 8.4  Custom Instructions eingefügt       [x]
□ 8.5  Erster Test: Planer liest Dateien    [ ]

PHASE 9: EIGENER TEST (vorher 8)          Status
─────────────────────────────────────────────────
□ 9.1  Produkt-Repo erstellt                [ ]
□ 9.2  client.json für eigenes Projekt      [ ]
□ 9.3  Eigene Automation zusammengesteckt   [ ]
□ 9.4  Lokal getestet                       [ ]
□ 9.5  Deployed                             [ ]
□ 9.6  VERBESSERUNGEN.md geschrieben        [ ]
□ 9.7  Alle Fixes zurück ins Core/Blocks    [ ]
□ 9.8  v0.2 getaggt                         [ ]

PHASE 10: ERSTES KUNDEN-PRODUKT           Status
─────────────────────────────────────────────────
□ 10.1 Produkt-Repo                         [ ]
□ 10.2 Alle Automationen als Blocks         [ ]
□ 10.3 client.json Template                 [ ]
□ 10.4 Lokal getestet                       [ ]
□ 10.5 Erster Kunde: Repo + Deploy          [ ]
□ 10.6 Erster Kunde: Onboarding             [ ]

PHASE 11: STABILISIERUNG                  Status
─────────────────────────────────────────────────
□ 11.1 Kunden-Feedback einarbeiten          [ ]
□ 11.2 Kosten-Tracking Modul               [ ]
□ 11.3 Update-Skript (update_all.sh)        [ ]
□ 11.4 Kunden-Anleitung + Checklisten       [ ]
□ 11.5 v1.0 getaggt                         [ ]
```

---

# TEIL D: ARCHITEKTUR

## Zwei-Gehirne-System

```
┌──────────────────────────────────────────────────┐
│  PLANER (Claude.ai Project)                      │
│  Liest live via GitHub Pages:                    │
│  ├── AGENTCORE24.md         ← Dieses Dokument   │
│  ├── system_memory.json     ← Gelerntes          │
│  ├── blocks_library.json    ← Bausteine          │
│  └── agents_library.json    ← Patterns           │
│                                                  │
│  Ergebnis: Angebote + Claude Code Prompts        │
│  Lernt automatisch: Grischas Muster,             │
│  bewährte Fragen, Angebots-Stil                  │
└────────────────┬─────────────────────────────────┘
                 │ Copy-Paste Prompts
                 ▼
┌──────────────────────────────────────────────────┐
│  UMSETZER (Claude Code in Warp)                  │
│  Liest lokal: AGENTCORE24.md, CLAUDE.md,         │
│  system_memory.json                              │
│                                                  │
│  Schreibt zurück (git push):                     │
│  ├── system_memory.json     ← Learnings          │
│  ├── blocks_library.json    ← Neue Blocks        │
│  ├── agents_library.json    ← Neue Patterns      │
│  └── AGENTCORE24.md         ← Fortschritt        │
│                                                  │
│  Lernt automatisch: Block-Probleme,              │
│  Deployment-Issues, Code-Regeln                  │
└────────────────┬─────────────────────────────────┘
                 │ git push
                 ▼
        GitHub Pages (auto-sync, 1-2 Min)
                 │
                 ▼
        Planer liest beim nächsten Chat
        die neuesten Daten
```

## Drei Code-Schichten

```
automation-core/ (GitHub Repo + Pages)
├── AGENTCORE24.md              ← Dieses Dokument (alles in einem)
├── system_memory.json          ← Das lernende Gedächtnis
├── CLAUDE.md                   ← Regeln für Claude Code
└── core/                       ← Backend-Code

automation-blocks/ (GitHub Repo + Pages)
├── blocks_library.json         ← Block-Katalog
├── agents_library.json         ← Pattern-Katalog
└── blocks/                     ← Block-Code

Kunden-Projekte (je ein Repo)
├── core/                       ← Git Subtree aus automation-core
├── blocks/                     ← Git Subtree aus automation-blocks
├── config/client.json          ← Steuert Automationen
├── config/custom_prompts/      ← Kunden-Prompts
├── CLAUDE.md                   ← Projekt-Regeln
└── .env                        ← Keys, Passwörter
```

---

# TEIL E: KUNDEN-ABLAUF (Phase A bis H)

## Übersicht

```
A: VERSTEHEN  → Erstgespräch, Schmerzpunkte notieren
B: PLANEN     → Im Planer (Claude.ai), Angebot + Bauplan erstellen
C: INFRA      → Server/Coolify einrichten (Claude Code)
D: ENTDECKEN  → CRM-Felder auslesen mit temporärem Kunden-Key
E: BAUEN      → Claude Code Prompts vom Planer reinkopieren
F: ÜBERGABE   → Screen-Share, Kunde erstellt NEUE Keys
G: BETRIEB    → Monitoring, Support bei Problemen
H: LERNEN     → system_memory.json wird automatisch aktualisiert
```

## Phase A: Verstehen (30-60 Min, Gespräch)

Du fragst: Zeitfresser? Tools? Teamgrösse? API-Erfahrung?
Du notierst: Branche, Schmerzpunkte, Tools, technisches Level.

## Phase B: Planen (30-60 Min, Planer in Claude.ai)

```
"Neuer Kunde: [NAME], [BRANCHE], [TEAM].
Schmerzpunkte: [LISTE]
Tools: [LISTE]"
```

Planer liest automatisch system_memory.json + Libraries.
Erstellt Angebot → Kunde sagt ja → Planer erstellt Bauplan mit 4 Claude Code Prompts.

## Phase C: Infrastruktur (30 Min, Claude Code)

Server/App in Coolify, Domain, UptimeRobot.

## Phase D: Entdecken (30-60 Min, Claude Code + Kunden-Keys)

```
DEINE KEYS: OpenAI, Anthropic, Slack (Test), Gmail (Test)
VOM KUNDEN: Sein CRM, branchenspezifische Software
```

Sage Kunden: "Erstelle temporären Key. Nach Einrichtung löschst du ihn und erstellst einen neuen."

Claude Code liest CRM-Struktur aus (NUR lesen). Erstellt Field-Mapping.

## Phase E: Bauen + Testen (2-4 Std, Claude Code)

4 Prompts vom Planer nacheinander reinkopieren.
Testen mit eigenen Keys + Kunden-Keys.
Danach: ALLE Keys entfernen.

## Phase F: Übergabe (30-45 Min, Screen-Share)

Kunde löscht alten Key → erstellt neuen → trägt im Dashboard ein → gemeinsam testen.

## Phase G: Betrieb (15-30 Min/Monat)

UptimeRobot prüfen. Bei Problemen: Claude Code debuggt und fixt.

## Phase H: Lernen (automatisch)

Claude Code aktualisiert system_memory.json automatisch mit allem was er erkennen kann.
Stellt Grischa EINE kurze Frage: "War der Kunde zufrieden?"

## Checkliste pro Kunde

```
□ A: Erstgespräch geführt, Infos notiert
□ B: Planer hat Angebot + Bauplan erstellt, Kunde zugesagt
□ C: Server/Coolify/Domain/Monitoring eingerichtet
□ D: Kunden-Keys erhalten, CRM-Struktur ausgelesen, Mapping erstellt
□ E: 4 Prompts in Claude Code, gebaut + getestet, alle Keys entfernt
□ F: Übergabe-Call, Kunde hat neue Keys, alles läuft
□ G: System läuft, Monitoring aktiv, Rechnung verschickt
□ H: system_memory.json aktualisiert
```

---

# TEIL F: PLANUNGS-SYSTEM (Custom Instructions für Claude.ai Project)

Diese Custom Instructions in das Claude.ai Project "AgentCore24 Planer" kopieren:

```markdown
# AgentCore24 Planer — System Instructions

## Wer du bist
Du bist Grischas technischer Planungs-Assistent für "AgentCore24".
Du PLANST. Du baust NICHT. Claude Code baut.
Grischa ist kein Entwickler. Erkläre alles in normaler Sprache.

## Vor jeder Antwort lesen (PFLICHT)

Lies diese Dateien via web_fetch:
1. https://gkaltenbacher-ux.github.io/automation-core/system_memory.json
2. https://gkaltenbacher-ux.github.io/automation-blocks/blocks_library.json
3. https://gkaltenbacher-ux.github.io/automation-blocks/agents_library.json
4. https://gkaltenbacher-ux.github.io/automation-core/AGENTCORE24.md

Sage kurz: "[System gelesen: X Blocks, Y Patterns. Memory: Z Kunden-Erfahrungen.]"

Nutze system_memory.json für:
- about_grischa → Kommunikationsstil anpassen
- kunden_erfahrungen → Bewährte Patterns vorschlagen, vor Problemen warnen
- system_learnings → Optimierte Block-Configs empfehlen
- planer_optimierungen → Angebots-Stil, bewährte Fragen

## Automatisches Lernen im Planer
Du erkennst selbst Muster:
- Welche Option Grischa meistens wählt → beim nächsten Mal zuerst zeigen
- Welche Rückfragen er immer gleich beantwortet → nicht mehr stellen
- Wie er Angebote umformuliert → Format anpassen

Am Ende jeder Planungs-Session: Füge im letzten Claude Code Prompt hinzu:
"Aktualisiere system_memory.json: planer_optimierungen + about_grischa"

## Modus A: Angebot erstellen
Trigger: "Neuer Kunde" + Infos
1. Dateien lesen, Branche in system_memory.json prüfen
2. Rückfragen stellen (Schmerzpunkte, Tools, Ziel, Budget)
3. 2-3 Optionen zeigen mit Vor-/Nachteilen
4. Gemeinsam verfeinern bis Grischa sagt "passt"
5. Angebot generieren (kurz, Kosten in CHF, kein Jargon)

## Modus B: Bauplan erstellen
Trigger: "Kunde hat zugesagt" + CRM-Infos
1. client.json erstellen (gültiges JSON)
2. Prompt-Dateien für Sub-Agents
3. 4 Copy-Paste Prompts für Claude Code
4. Test-Checkliste + Übergabe-Anleitung
WICHTIG: Jeder Prompt muss eigenständig verständlich sein für Claude Code.

## Modus C: Erweiterung planen
Trigger: "Kunde X will noch Y"
Prüfe Blocks + system_memory.json → Erweiterung oder neuer Block.

## Modus D: System verbessern
Trigger: "Was können wir verbessern?"
Lies system_memory.json → Vorschläge für neue Blocks, Optimierungen, Pricing.

## Regeln
- Deutsch, informell mit Grischa. Professionell (Sie) in Kunden-Docs.
- Kosten: CHF für Setup, EUR für API-Kosten
- Günstigstes Modell zuerst (gpt-4o-mini vor gpt-4o)
- Block "status: planned" → erwähne dass er erst gebaut werden muss
```

---

# TEIL G: CLAUDE.md TEMPLATE

Wird in jedes Kunden-Projekt kopiert:

```markdown
# CLAUDE.md — Projekt-Regeln

## Projekt
Automations-Plattform für [KUNDENNAME].
Core → Blocks → Config.

## Stack (NUR diese — KEINE anderen)
- Backend: FastAPI (Python 3.11+). NICHT Flask. NICHT Django.
- Datenbank: SQLite mit Write-Queue. NICHT PostgreSQL. NICHT MongoDB.
- Dashboard: EINE HTML-Datei, Tailwind + Alpine.js. NICHT React. KEIN Build-Step.
- Scheduling: APScheduler. NICHT Celery.
- Verschlüsselung: Fernet. Container: Docker Compose.

## Regeln
- core/ = ALLE Kunden gleich. NIEMALS kunden-spezifisches rein.
- blocks/ = Wiederverwendbar. NIEMALS kunden-spezifisches rein.
- config/ = Kunden-spezifisch. NIE durch Updates überschreiben.
- Block-Interface: async def execute(input_data, config, context) -> dict
- Logging: NORMALE SPRACHE, kein Tech-Jargon
- API-Keys: IMMER via context["get_api_key"](), NIEMALS hardcoden

## System-Memory Pflege
Bei neuem Block → blocks_library.json aktualisieren + git push
Bei neuem Pattern → agents_library.json aktualisieren + git push
Nach Projekt → system_memory.json automatisch aktualisieren + git push
```

---

# TEIL H: KOSTEN UND PRICING

## Pro Kunde
| Posten | Monatlich |
|---|---|
| Hetzner CX22 + Snapshots | ~€4.55 |
| Coolify + SSL + UptimeRobot | €0 |
| **Gesamt** | **~€5-6** |

## Dein Pricing
| Leistung | Preis |
|---|---|
| Setup + Basis-Automationen | CHF 1'500-3'000 |
| Monatliche Betreuung | CHF 200-500/Monat |
| Erweiterungsmodul | CHF 500-2'000 |
| Neue Automation | CHF 300-800 |

---

# TEIL I: HILFE

**Claude Code:** "Wo stehen wir?" oder "Ich stecke fest bei [X]."
**Planer:** "Ich verstehe [X] nicht. Erkläre es mir einfach."
**Beide:** "Lies system_memory.json — hatten wir das Problem schon?"

---

# SESSION-LOG

- 2026-03-27 — Phase 1-7 komplett. Live auf https://agentcore24.com. v0.1 getaggt.
- 2026-03-28 — Phase 8 (Planungs-System) gestartet. system_memory.json im Repo. Claude.ai Planer-Projekt erstellt + Custom Instructions eingefügt.
