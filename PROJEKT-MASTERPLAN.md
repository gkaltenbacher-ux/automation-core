# PROJEKT-MASTERPLAN: Automations-Plattform für Consulting
# Version 6.0 — Mit selbstlernendem System
# Stand: März 2026

---

## FÜR CLAUDE CODE: Lies diesen Abschnitt zuerst

Dieses Dokument ist der komplette Projektplan für Grischa's Automations-Consulting-Business AgentCore24.

### ÜBER GRISCHA

Lies IMMER zuerst `system_memory.json` im automation-core Repo.
Dort steht alles was das System über Grischas Arbeitsweise gelernt hat.
Falls die Datei nicht erreichbar ist, gelten diese Grundregeln:

- Grischa ist KEIN Entwickler. Er kann keinen Code lesen oder schreiben.
- Erkläre jeden Schritt so dass ein Nicht-Techniker ihn versteht.
- Mache technische Schritte selbst, frage nicht ob Grischa sie manuell machen will.
- Grischa arbeitet mit Warp als Terminal.
- Grischa kommuniziert auf Deutsch, oft informell.
- Wenn Grischa sagt "mach das", dann mach es — frage nicht dreimal nach.

### ROLLEN

- **Deine Rolle:** Du bist Architekt, Entwickler, Tester und Debugger.
- **Grischas Rolle:** Er beschreibt Anforderungen, prüft im Browser, gibt Feedback.

### REGELN

- Erkläre jeden Schritt bevor du ihn ausführst
- Teste nach jedem Build-Schritt automatisch
- Mache nie mehr als einen Schritt auf einmal ohne Bestätigung
- Schreibe Log-Nachrichten und Dashboard-Texte immer auf Deutsch
- Wenn Grischa fragt "wo stehen wir?", schau in den Fortschritts-Tracker

### AUTO-UPDATE (nach JEDEM abgeschlossenen Schritt, ohne zu fragen)

Nach jedem abgeschlossenen Schritt aktualisierst du sofort:

1. **PROJEKT-MASTERPLAN.md:** Hake Schritt ab, notiere Infos (IPs, URLs, Entscheidungen)
2. **SESSION-LOG:** Ergänze was geschafft wurde
3. **system_memory.json:** Ergänze neue Erkenntnisse:
   - `about_grischa.gelernt` → Wenn du etwas Neues über seine Arbeitsweise gelernt hast
   - `system_learnings.blocks` → Wenn ein Block Probleme hatte oder optimiert wurde
   - `system_learnings.claude_code_regeln` → Wenn du eine neue Best-Practice entdeckt hast
   - `kunden_erfahrungen` → Nach jedem Kunden-Projekt
4. **blocks_library.json:** Wenn du einen neuen Block gebaut hast
5. **agents_library.json:** Wenn du ein neues Pattern implementiert hast
6. Du fragst NICHT ob du das tun sollst — du tust es einfach
7. git commit + push nach jedem Update

### NACH JEDEM ABGESCHLOSSENEN KUNDEN-PROJEKT

Frage Grischa: "Was haben wir bei diesem Projekt gelernt?"
Aktualisiere system_memory.json mit:
- Branche + typische Schmerzpunkte in `kunden_erfahrungen`
- Probleme und Lösungen in `system_learnings`
- Neue Präferenzen in `about_grischa`
- Bewährte Patterns und Pricing in `kunden_erfahrungen.branchen`

---

## SESSION-LOG

Format: Datum — Was geschafft — Wichtige Infos

- 2026-03-27 — Phase 1-6 komplett. Phase 7 komplett: App deployed + SSL live auf https://agentcore24.com. v0.1 getaggt.

---

## 1. DAS PROJEKT IN EINEM SATZ

Grischa baut mit Claude Code Automations-Systeme für Kunden. Jeder Kunde bekommt ein Dashboard wo er API-Keys einträgt und seine Automationen sieht. Die Automationen werden aus wiederverwendbaren Bausteinen zusammengesteckt. Das System lernt mit jedem Projekt dazu.

---

## 2. KERN-PRINZIPIEN (ändern sich nie)

**Prinzip 1: Zwei Gehirne, ein System**
Planer (Claude.ai) plant und erstellt Baupläne. Umsetzer (Claude Code) baut und deployt. Beide lesen die gleichen Dateien (system_memory.json, blocks_library.json, agents_library.json). Was einer lernt, weiss der andere sofort.

**Prinzip 2: Drei Schichten**
Core (alle Kunden gleich) → Blocks (wiederverwendbare Bausteine) → Config (kunden-spezifisch). Updates am Core oder an Blocks gehen per Skript an alle Kunden.

**Prinzip 3: Konfiguration statt Code**
Neue Kunden-Projekte werden konfiguriert, nicht programmiert. Die client.json steuert welche Bausteine laufen.

**Prinzip 4: Dashboard bleibt HTML**
Eine HTML-Datei, Tailwind + Alpine.js via CDN. Kein React, kein Build-Step.

**Prinzip 5: BYOK (Bring Your Own Key)**
Der Kunde zahlt seine eigenen API-Kosten.

**Prinzip 6: Das System lernt**
system_memory.json wird nach jedem Projekt, jedem Bug-Fix, jeder Erkenntnis aktualisiert. Der Planer und Claude Code lesen sie. Das System wird mit jedem Kunden besser.

---

## 3. FORTSCHRITTS-TRACKER

```
PHASE 1: INFRASTRUKTUR                    Status
─────────────────────────────────────────────────
✅ 1.1  Hetzner Server bestellen            [x] → 178.104.122.219
✅ 1.2  Coolify installieren                [x]
✅ 1.3  Coolify einrichten + GitHub          [x]
✅ 1.4  Hetzner Snapshots aktivieren         [x]
✅ 1.5  UptimeRobot Account erstellen        [x]

PHASE 2: REPOS ERSTELLEN                   Status
─────────────────────────────────────────────────
✅ 2.1  GitHub Repo "automation-core"        [x] → gkaltenbacher-ux/automation-core
✅ 2.2  GitHub Repo "automation-blocks"      [x] → gkaltenbacher-ux/automation-blocks
✅ 2.3  Ordnerstrukturen anlegen             [x]
✅ 2.4  CLAUDE.md erstellen (Core)           [x]
✅ 2.5  CLAUDE.md erstellen (Blocks)         [x]
✅ 2.6  Erster Commit + Push beider Repos    [x]

PHASE 3: CORE BAUEN                       Status
─────────────────────────────────────────────────
✅ 3.1-3.10 Alle Core-Dateien               [x]

PHASE 4: DASHBOARD BAUEN                  Status
─────────────────────────────────────────────────
✅ 4.1-4.5 Dashboard komplett               [x]

PHASE 5: ERSTE BAUSTEINE                  Status
─────────────────────────────────────────────────
✅ 5.1-5.6 Alle 6 Basis-Blocks             [x]

PHASE 6: LOKAL TESTEN                     Status
─────────────────────────────────────────────────
✅ 6.1-6.8 Alle Tests bestanden             [x]

PHASE 7: ERSTER DEPLOY                    Status
─────────────────────────────────────────────────
✅ 7.1-7.5 Live auf https://agentcore24.com [x] → v0.1

PHASE 8: EIGENER TEST                     Status
─────────────────────────────────────────────────
□ 8.1  Produkt-Repo erstellt                [ ]
□ 8.2  client.json für eigenes Projekt      [ ]
□ 8.3  Eigene Automation zusammengesteckt   [ ]
□ 8.4  Lokal getestet                       [ ]
□ 8.5  Deployed                             [ ]
□ 8.6  VERBESSERUNGEN.md geschrieben        [ ]
□ 8.7  Alle Fixes zurück ins Core/Blocks    [ ]
□ 8.8  v0.2 getaggt                         [ ]

PHASE 9: ERSTES KUNDEN-PRODUKT            Status
─────────────────────────────────────────────────
□ 9.1  Produkt-Repo                         [ ]
□ 9.2  Alle Automationen als Blocks         [ ]
□ 9.3  client.json Template                 [ ]
□ 9.4  Lokal getestet                       [ ]
□ 9.5  Erster Kunde: Repo + Deploy          [ ]
□ 9.6  Erster Kunde: Onboarding             [ ]

PHASE 10: STABILISIERUNG                  Status
─────────────────────────────────────────────────
□ 10.1 Kunden-Feedback einarbeiten          [ ]
□ 10.2 Kosten-Tracking Modul               [ ]
□ 10.3 Update-Skript (update_all.sh)        [ ]
□ 10.4 Kunden-Anleitung                     [ ]
□ 10.5 Coolify-Notfall-Checkliste           [ ]
□ 10.6 v1.0 getaggt                         [ ]

PHASE 11: PLANUNGS-SYSTEM                 Status
─────────────────────────────────────────────────
□ 11.1 system_memory.json ins Core-Repo     [ ]
□ 11.2 GitHub Pages aktivieren (beide Repos)[ ]
□ 11.3 Claude.ai Project "Planer" erstellen [ ]
□ 11.4 Custom Instructions einfügen         [ ]
□ 11.5 Erster Test: Planer liest Dateien    [ ]
□ 11.6 Erster Test: Planer erstellt Angebot [ ]
```

---

## 4. ARCHITEKTUR

### 4.1 Das Zwei-Gehirne-System

```
┌─────────────────────────────────────────────────────────┐
│  PLANER (Claude.ai Project)                             │
│  Liest live via GitHub Pages:                           │
│  ├── system_memory.json    ← Was das System gelernt hat │
│  ├── blocks_library.json   ← Verfügbare Bausteine      │
│  ├── agents_library.json   ← Standard-Patterns         │
│  ├── PROJEKT-MASTERPLAN.md ← Projekt-Status             │
│  └── KUNDEN-ABLAUF.md      ← Prozess-Vorgaben          │
│                                                         │
│  Ergebnis: Angebote, Baupläne, Claude Code Prompts      │
└────────────────────┬────────────────────────────────────┘
                     │ Copy-Paste Prompts
                     ▼
┌─────────────────────────────────────────────────────────┐
│  UMSETZER (Claude Code in Warp)                         │
│  Liest lokal:                                           │
│  ├── PROJEKT-MASTERPLAN.md                              │
│  ├── CLAUDE.md                                          │
│  └── system_memory.json                                 │
│                                                         │
│  Schreibt zurück (git push):                            │
│  ├── system_memory.json    ← Neue Learnings             │
│  ├── blocks_library.json   ← Neue Blocks                │
│  ├── agents_library.json   ← Neue Patterns              │
│  └── PROJEKT-MASTERPLAN.md ← Fortschritt                │
│                                                         │
│  Ergebnis: Fertiger Code, getestet, deployed            │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
          ┌──────────────────┐
          │  GitHub Pages     │
          │  (auto-sync)      │
          │  1-2 Min nach     │
          │  git push         │
          └──────────────────┘
                     │
                     ▼
          Planer liest beim nächsten
          Gespräch die neuesten Daten
```

### 4.2 Die drei Code-Schichten

```
SCHICHT 1 — "Core" (Repo: automation-core)
├── Backend-Infrastruktur (ALLE Kunden gleich)
├── system_memory.json (das lernende Gedächtnis)
├── PROJEKT-MASTERPLAN.md
└── KUNDEN-ABLAUF.md

SCHICHT 2 — "Blocks" (Repo: automation-blocks)
├── Wiederverwendbare Automations-Bausteine
├── blocks_library.json (Block-Katalog)
└── agents_library.json (Pattern-Katalog)

SCHICHT 3 — "Config" (Pro Kunde einzigartig)
├── client.json (steuert alles)
├── custom_prompts/ (Kunden-Prompts)
└── .env (Keys, Passwörter)
```

### 4.3 Wie ein Kunden-Projekt aussieht

```
kunde-hrsolutions/
├── core/                        ← Git Subtree aus automation-core
├── blocks/                      ← Git Subtree aus automation-blocks
├── config/
│   ├── client.json              ← Steuert Automationen
│   └── custom_prompts/          ← Kunden-spezifische Prompts
├── CLAUDE.md                    ← Projekt-Regeln
└── .env                         ← Kunden-spezifisch
```

---

## 5. CLAUDE.md TEMPLATE (für jedes Projekt)

```markdown
# CLAUDE.md — Projekt-Regeln

## Projekt
Automations-Plattform für [KUNDENNAME].
Drei-Schichten-Architektur: Core → Blocks → Config.

## Stack (NUR diese — KEINE anderen)
- Backend: FastAPI (Python 3.11+). NICHT Flask. NICHT Django.
- Datenbank: SQLite mit Write-Queue. NICHT PostgreSQL. NICHT MongoDB.
- Dashboard: EINE HTML-Datei, Tailwind + Alpine.js via CDN. NICHT React. NICHT Vue. KEIN Build-Step.
- Scheduling: APScheduler. NICHT Celery.
- Verschlüsselung: Fernet. NICHT eigene Crypto.
- Container: Docker Compose. NICHT Kubernetes.

## Architektur-Regeln
- core/ = ALLE Kunden gleich. NIEMALS kunden-spezifisches rein.
- blocks/ = Wiederverwendbar. NIEMALS kunden-spezifisches rein.
- config/ = Kunden-spezifisch. Wird NIE durch Updates überschrieben.
- Block-Interface: async def execute(input_data, config, context) -> dict
- Logging: NORMALE SPRACHE, kein Tech-Jargon
- API-Keys: IMMER via context["get_api_key"](), NIEMALS hardcoden

## System-Memory Pflege (WICHTIG)
Lies system_memory.json im automation-core Repo für Kontext.

Nach JEDEM neuen Block:
1. Block in blocks/ erstellen
2. blocks_library.json aktualisieren (neuer Eintrag + statistics)
3. git commit + push

Nach JEDEM neuen Agent-Pattern:
1. agents_library.json aktualisieren
2. git commit + push

Nach JEDEM abgeschlossenen Projekt:
1. Frage Grischa: "Was haben wir gelernt?"
2. system_memory.json aktualisieren
3. git commit + push

GRUND: Der Planer-Claude liest diese Dateien live.
Ohne Updates kennt er neue Blocks und Learnings nicht.
```

---

## 6. DATEIEN-ÜBERSICHT (was wo lebt)

```
automation-core/ (GitHub Repo + GitHub Pages)
├── PROJEKT-MASTERPLAN.md        ← Projekt-Status + Fortschritt
├── KUNDEN-ABLAUF.md             ← Kunden-Prozess A-G
├── system_memory.json           ← Das lernende Gedächtnis ⭐
└── core/                        ← Backend-Code

automation-blocks/ (GitHub Repo + GitHub Pages)
├── blocks_library.json          ← Block-Katalog
├── agents_library.json          ← Pattern-Katalog
└── blocks/                      ← Block-Code

Claude.ai Project "AgentCore24 Planer"
└── Custom Instructions          ← Liest alles live aus Repos

~/Projects/ (lokal)
├── automation-core/
├── automation-blocks/
└── kunde-xyz/

iCloud Drive/AgentCore24/
└── PROJEKT-MASTERPLAN.md        ← Backup
```

---

## 7. KOSTEN

### Pro Kunde
| Posten | Monatlich |
|---|---|
| Hetzner CX22 | €4.35 |
| Hetzner Snapshots | ~€0.20 |
| Coolify + SSL + UptimeRobot | €0 |
| **Gesamt** | **~€5-6** |

### Dein Pricing
| Leistung | Preis |
|---|---|
| Setup + Basis-Automationen | CHF 1'500-3'000 |
| Monatliche Betreuung | CHF 200-500/Monat |
| Erweiterungsmodul | CHF 500-2'000 |
| Neue Automation | CHF 300-800 |

---

## 8. WENN DU FESTSTECKST

```
"Wo stehen wir? Lies den Fortschritts-Tracker."
"Ich stecke fest bei Schritt [X]. Hilf mir."
"Lies system_memory.json — haben wir das Problem schon mal gehabt?"
```
