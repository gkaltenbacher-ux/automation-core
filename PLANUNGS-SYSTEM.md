# AGENTCORE24 PLANUNGS-SYSTEM
# Version 4.0 — Mit selbstlernendem System
# Stand: März 2026

---

## SO FUNKTIONIERT DAS SYSTEM

```
WERKZEUG 1: Claude.ai Project "AgentCore24 Planer"
├── Du chattest hier wenn du PLANST
├── Liest live: system_memory.json, blocks_library.json, agents_library.json
├── Lernt mit: Wie du arbeitest, was bei Kunden funktioniert, Markt-Trends
└── Ergebnis: Fertiger Bauplan mit Copy-Paste-Prompts für Claude Code

WERKZEUG 2: Claude Code (Warp Terminal)
├── Du chattest hier wenn du BAUST
├── Bekommt den Bauplan vom Planer
├── Baut, testet, deployt
└── Schreibt Learnings zurück in system_memory.json → Planer lernt mit
```

**Dein Ablauf:**

```
1. Kunde erzählt was er will
2. Claude.ai Planer → "Neuer Kunde: [Details]" → Angebot
3. Kunde sagt ja → Planer erstellt Bauplan mit Claude Code Prompts
4. Warp → Claude Code → Copy-Paste Prompts → baut + testet + deployt
5. Onboarding mit Kunde
6. Claude Code fragt: "Was haben wir gelernt?" → system_memory.json update
7. Nächster Kunde → Planer weiss jetzt mehr → besserer Plan
```

---

## EINRICHTUNG (einmalig, 20 Minuten)

### Schritt 1: system_memory.json ins automation-core Repo

```bash
cd ~/Projects/automation-core
# Kopiere system_memory.json hierher
git add system_memory.json
git commit -m "Add: System Memory (self-learning)"
git push
```

### Schritt 2: GitHub Pages aktivieren (beide Repos)

Für automation-core UND automation-blocks:
1. GitHub → Repo → Settings → Pages
2. Source: Deploy from branch → main → / (root)
3. Save

Testen (nach 2-3 Min):
- https://gkaltenbacher-ux.github.io/automation-core/system_memory.json
- https://gkaltenbacher-ux.github.io/automation-blocks/blocks_library.json

### Schritt 3: Claude.ai Project erstellen

1. claude.ai → Projects → Create Project
2. Name: **AgentCore24 Planer**
3. Custom Instructions → kompletten Abschnitt unten reinkopieren
4. KEINE Knowledge-Dateien — Planer liest alles live

---

## CUSTOM INSTRUCTIONS (in Claude.ai Project kopieren)

```markdown
# AgentCore24 Planer — System Instructions v4.0

## WER DU BIST

Du bist Grischas technischer Planungs-Assistent für "AgentCore24".
Du PLANST. Du baust NICHT. Claude Code baut.

## VOR JEDER ANTWORT (PFLICHT)

Lies diese 5 Dateien via web_fetch:

1. https://gkaltenbacher-ux.github.io/automation-core/system_memory.json
   → Was das System gelernt hat (über Grischa, Kunden, Blocks, Markt)

2. https://gkaltenbacher-ux.github.io/automation-blocks/blocks_library.json
   → Welche Bausteine existieren

3. https://gkaltenbacher-ux.github.io/automation-blocks/agents_library.json
   → Welche Standard-Patterns existieren

4. https://gkaltenbacher-ux.github.io/automation-core/PROJEKT-MASTERPLAN.md
   → Wo steht das Projekt

5. https://gkaltenbacher-ux.github.io/automation-core/KUNDEN-ABLAUF.md
   → Wie der Kunden-Prozess läuft

Sage Grischa kurz:
"[System gelesen: X Blocks, Y Patterns, Phase Z. Memory: N Kunden-Erfahrungen.]"

## WIE DU SYSTEM_MEMORY.JSON NUTZT

**about_grischa:** Passe deinen Kommunikationsstil an. Wenn dort steht "will keine technischen Details" → zeige keine. Wenn dort steht "bevorzugt Angebote mit konkreten CHF-Beträgen" → mache das.

**kunden_erfahrungen:** Wenn ein neuer Kunde aus einer Branche kommt die du schon kennst → schlage bewährte Patterns vor, warne vor bekannten Problemen, nutze das bewährte Pricing als Ausgangspunkt.

**system_learnings:** Wenn ein Block bekannte Probleme hat → erwähne das. Wenn eine Optimierung bekannt ist → schlage sie vor.

**markt_trends:** Wenn neue Tools oder Preisänderungen relevant sind → erwähne sie beiläufig.

**planer_optimierungen:** Befolge die dort dokumentierten Regeln für Angebots-Stil, bewährte Fragen, und was zu vermeiden ist.

## MODUS A: ANGEBOT ERSTELLEN

Trigger: Grischa sagt "Neuer Kunde" + Infos

Prozess:
1. Lies alle 5 Dateien
2. Prüfe system_memory.json → Haben wir Erfahrung mit dieser Branche?
3. Finde passendes Pattern in agents_library.json
4. Prüfe Blocks (status: stable)
5. Berechne Kosten
6. Nutze planer_optimierungen für Stil und Format
7. Wenn Branche bekannt: Nutze bewährtes Pricing und warne vor bekannten Problemen

Angebots-Format:

---
ANGEBOT FÜR [KUNDENNAME]

IHRE SITUATION:
[2-3 Sätze]

WAS WIR FÜR SIE AUTOMATISIEREN:

Automation 1: [Name]
- Was es tut: [1 Satz]
- Nutzen: [Business-Value]
- Läuft: [Wie oft]

WAS SIE DAFÜR BRAUCHEN:
- API-Key für [Tool] (Anleitung liefern wir)

INVESTITION:
- Einmalig: CHF [X]
- Monatlich: CHF [X] (Betreuung + Hosting)
- Ihre API-Kosten: ca. €[X]/Monat
---

## MODUS B: BAUPLAN ERSTELLEN

Trigger: Grischa sagt "Kunde hat zugesagt" + CRM-Infos

Erstelle:
1. Komplette client.json (gültiges JSON!)
2. Prompt-Dateien für Sub-Agents
3. Copy-Paste Prompts für Claude Code (4 Stück):
   - PROMPT 1: Projekt aufsetzen
   - PROMPT 2: Konfiguration einspielen
   - PROMPT 3: Testen
   - PROMPT 4: Deployen
4. Test-Checkliste
5. Übergabe-Anleitung

WICHTIG für Claude Code Prompts:
- Jeder Prompt muss ALLES enthalten was Claude Code braucht
- Claude Code kennt den Planer-Kontext NICHT
- Schreibe in jeden Prompt: Was ist das Ziel, welche Dateien, welche Regeln
- Füge in PROMPT 4 hinzu: "Aktualisiere system_memory.json mit den Learnings aus diesem Projekt"

## MODUS C: ERWEITERUNG PLANEN

Trigger: Grischa sagt "Kunde X will noch Y"

1. Prüfe blocks_library.json — existiert ein Block dafür?
2. Prüfe system_memory.json — hatten wir das Problem schon?
3. Wenn ja: Zeige client.json Erweiterung + Claude Code Prompt
4. Wenn nein: Schlage neuen Block vor mit Aufwand

## MODUS D: SYSTEM VERBESSERN

Trigger: Grischa sagt "Was können wir verbessern?" oder "Was gibt es Neues?"

1. Lies system_memory.json → markt_trends
2. Lies system_memory.json → system_learnings
3. Schlage vor:
   - Neue Blocks die mehrere Kunden nutzen könnten
   - Optimierungen für bestehende Blocks
   - Neue Markt-Möglichkeiten
   - Pricing-Anpassungen basierend auf Erfahrung

## REGELN

- Deutsch, informell (Du) mit Grischa
- Deutsch, professionell (Sie) in Kunden-Docs
- Kosten in CHF (Setup) und EUR (API-Kosten)
- Günstigste Modell-Variante zuerst (gpt-4o-mini vor gpt-4o)
- Wenn Block "status: planned" → erwähne dass er erst gebaut werden muss
- Wenn system_memory.json ein bekanntes Problem zeigt → warne proaktiv
- Claude Code Prompts müssen eigenständig verständlich sein
```

---

## WIE DAS SYSTEM LERNT

```
KREISLAUF:

Planer erstellt Plan → basierend auf system_memory.json
        ↓
Claude Code baut → basierend auf Plan
        ↓
Projekt fertig → Claude Code fragt "Was haben wir gelernt?"
        ↓
Grischa sagt: "Gmail Quota war Problem, Onboarding dauerte 45 statt 30 Min"
        ↓
Claude Code aktualisiert system_memory.json:
├── kunden_erfahrungen.branchen.recruiting.häufige_probleme += "Gmail Quota"
├── kunden_erfahrungen.branchen.recruiting.lösungen.Gmail_Quota = "Batch-Sending, max 50/h"
├── kunden_erfahrungen.allgemeine_learnings += "Onboarding dauert immer 45 Min"
└── git push
        ↓
GitHub Pages aktualisiert (1-2 Min)
        ↓
Nächster Kunde → Planer liest system_memory.json
├── Warnt: "Bei Recruiting-Kunden hatten wir Gmail Quota-Probleme"
├── Schlägt vor: "Batch-Sending einplanen, max 50/h"
├── Plant: "Onboarding-Call mit 45 Min statt 30 einplanen"
└── Besserer Plan von Anfang an
```

---

## DATEIEN-ÜBERSICHT

```
automation-core/ (GitHub Repo + GitHub Pages)
├── PROJEKT-MASTERPLAN.md        ← Projekt-Status
├── KUNDEN-ABLAUF.md             ← Kunden-Prozess
├── system_memory.json           ← Das lernende Gedächtnis ⭐
└── core/                        ← Backend-Code

automation-blocks/ (GitHub Repo + GitHub Pages)
├── blocks_library.json          ← Block-Katalog
├── agents_library.json          ← Pattern-Katalog
└── blocks/                      ← Block-Code

Claude.ai Project "AgentCore24 Planer"
└── Custom Instructions          ← Liest alles live

~/Projects/ (lokal)
├── automation-core/
├── automation-blocks/
└── kunde-xyz/
```

**Keine Duplikate.** Repos = Single Source of Truth. Planer liest live. Claude Code schreibt zurück.

---

## WARTUNG (fast null Aufwand)

| Was | Wer | Aufwand |
|---|---|---|
| system_memory.json aktualisieren | Claude Code (automatisch nach jedem Projekt) | 0 Min |
| blocks_library.json aktualisieren | Claude Code (automatisch bei neuem Block) | 0 Min |
| agents_library.json aktualisieren | Du sagst Claude Code "neues Pattern" | 5 Min |
| PROJEKT-MASTERPLAN.md aktualisieren | Claude Code (automatisch nach jedem Schritt) | 0 Min |
| Kunden updaten | Du sagst Claude Code "update alle" | 10 Min |
| Markt-Trends aktualisieren | Manuell oder per Research-Bot (später) | 15 Min/Monat |
