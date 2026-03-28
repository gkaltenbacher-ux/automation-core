# KUNDEN-ABLAUF: Vom Erstgespräch bis zum laufenden System
# Version 2.0 — Mit Planer-Integration und System-Memory
# Stand: März 2026

---

## ÜBERSICHT

```
PHASE A: VERSTEHEN        → Erstgespräch mit Kunde
PHASE B: PLANEN            → Im Planer (Claude.ai) — erstellt Angebot + Bauplan
PHASE C: INFRASTRUKTUR     → Server einrichten (Claude Code)
PHASE D: ENTDECKEN         → CRM/Tools auslesen (Claude Code mit Kunden-Keys)
PHASE E: BAUEN + TESTEN    → Claude Code baut nach Bauplan vom Planer
PHASE F: ÜBERGABE          → Kunde bekommt Zugang, erstellt NEUE Keys
PHASE G: BETRIEB           → Läuft, du kassierst monatlich
PHASE H: LERNEN            → system_memory.json wird aktualisiert ⭐ NEU
```

---

## PHASE A: VERSTEHEN (30-60 Min, Gespräch mit Kunde)

**Du fragst:**
- Was sind deine grössten Zeitfresser?
- Welche Tools nutzt du? (CRM, E-Mail, Chat, etc.)
- Wie viele Leute im Team?
- Hast du schon API-Zugänge?

**Du notierst:** Branche, Teamgrösse, Schmerzpunkte, Tools, technisches Level.

---

## PHASE B: PLANEN (30-60 Min, du + Planer in Claude.ai)

**NEU:** Planung passiert im **Planer** (Claude.ai Project), NICHT in Claude Code.

**Du in Claude.ai (AgentCore24 Planer):**
```
Neuer Kunde: [NAME], [BRANCHE], [TEAMGRÖSSE].
Schmerzpunkte: [LISTE]
Tools: [LISTE]
```

**Der Planer:**
1. Liest automatisch system_memory.json, blocks_library.json, agents_library.json
2. Prüft ob Erfahrung mit dieser Branche vorhanden (aus system_memory.json)
3. Findet passendes Pattern, prüft verfügbare Blocks
4. Warnt vor bekannten Problemen (aus system_memory.json)
5. Erstellt Angebot

**Wenn Kunde zusagt:**
```
Kunde hat zugesagt. Hier die CRM-Felder: [LISTE]
```

**Der Planer erstellt:**
- Komplette client.json
- Prompt-Dateien für Sub-Agents
- 4 Copy-Paste Prompts für Claude Code
- Test-Checkliste

---

## PHASE C: INFRASTRUKTUR (30 Min, Claude Code)

```
Schritt C.1 — Server/App in Coolify anlegen
Schritt C.2 — Domain zuweisen: kundenname.agentcore24.ch
Schritt C.3 — UptimeRobot Monitor einrichten
```

---

## PHASE D: ENTDECKEN (30-60 Min, Claude Code + Kunden-Keys)

### Keys die du brauchst:

```
DEINE EIGENEN (hast du schon):
✅ OpenAI, Anthropic, Slack (Test), Gmail (Test)

VOM KUNDEN (nur was du nicht selbst hast):
🔑 Sein CRM, seine branchenspezifische Software
```

### Wie du die Keys bekommst:

Sage dem Kunden: "Erstelle einen temporären API-Key. Nachdem alles eingerichtet ist, löschst du diesen und erstellst einen neuen."

### Was du damit machst:

Claude Code liest die Struktur des Kunden-CRM aus (Felder, IDs, Dropdown-Werte) und erstellt das Field-Mapping in der client.json.

---

## PHASE E: BAUEN + TESTEN (2-4 Stunden, Claude Code)

**Du kopierst die 4 Prompts vom Planer der Reihe nach in Claude Code.**

```
PROMPT 1 → Projekt aufsetzen
PROMPT 2 → client.json + Prompts einspielen
PROMPT 3 → Lokal testen (mit deinen Keys + Kunden-Keys)
PROMPT 4 → Deployen + system_memory.json aktualisieren
```

Nach dem Testen:
- ALLE Keys entfernen (deine + Kunden-Keys)
- Dashboard ist "leer" — bereit für Übergabe

---

## PHASE F: ÜBERGABE (30-45 Min, Screen-Share)

```
1. Dashboard zeigen
2. Kunde LÖSCHT alten Key (den du hattest)
3. Kunde erstellt NEUEN Key
4. Kunde trägt neuen Key im Dashboard ein
5. Gemeinsam testen
6. Fertig — du hast keinen Kunden-Key mehr
```

---

## PHASE G: BETRIEB (15-30 Min/Monat pro Kunde)

- UptimeRobot prüfen
- Gelegentlich Logs überfliegen
- Bei Problemen: Claude Code debuggt und fixt

---

## PHASE H: LERNEN (5 Min, nach jedem Projekt) ⭐ NEU

**Claude Code fragt dich:** "Projekt abgeschlossen. Was haben wir gelernt?"

**Du sagst z.B.:** "Gmail Quota war ein Problem. Onboarding dauerte 45 statt 30 Min. Der Kunde versteht 'Automation' besser als 'Agent'."

**Claude Code aktualisiert system_memory.json:**
```json
{
  "kunden_erfahrungen": {
    "branchen": {
      "recruiting": {
        "projekte": 1,
        "häufige_probleme": ["Gmail Quota-Limits"],
        "lösungen": {"Gmail Quota": "Batch-Sending, max 50/h"},
        "durchschnittlicher_setup": "4 Stunden",
        "durchschnittliches_pricing": "CHF 2500 Setup, CHF 350/Monat"
      }
    },
    "allgemeine_learnings": [
      "Onboarding dauert immer 45 Min, nie 30",
      "Kunden verstehen 'Automation' besser als 'Agent'"
    ]
  }
}
```

**git push → Planer weiss es beim nächsten Kunden.**

---

## CHECKLISTE: NEUER KUNDE

```
PHASE A: VERSTEHEN
□ Erstgespräch geführt
□ Schmerzpunkte, Tools, Team notiert

PHASE B: PLANEN (im Planer, Claude.ai)
□ Planer hat Angebot erstellt
□ Angebot an Kunde geschickt
□ Kunde hat zugesagt
□ Planer hat Bauplan + Claude Code Prompts erstellt

PHASE C: INFRASTRUKTUR
□ Server/App in Coolify
□ Domain zugewiesen
□ UptimeRobot Monitor

PHASE D: ENTDECKEN
□ Kunden-Keys erhalten (temporär)
□ CRM-Struktur ausgelesen
□ Field-Mapping erstellt

PHASE E: BAUEN + TESTEN
□ 4 Prompts in Claude Code kopiert
□ Alles gebaut und getestet
□ ALLE Keys entfernt

PHASE F: ÜBERGABE
□ Screen-Share mit Kunde
□ Kunde hat alte Keys gelöscht + neue erstellt
□ Alles läuft mit neuen Keys
□ Du hast KEINEN Kunden-Key mehr

PHASE G: BETRIEB
□ System läuft
□ Monitoring aktiv
□ Rechnung verschickt

PHASE H: LERNEN ⭐
□ "Was haben wir gelernt?" beantwortet
□ system_memory.json aktualisiert
□ git push gemacht
```

---

## DATENSCHUTZ

```
WÄHREND EINRICHTUNG: Du hast temporäre Kunden-Keys. Nur zum Lesen + Testen.
BEI ÜBERGABE: Kunde löscht alten Key, erstellt neuen. Du siehst ihn nie.
IM BETRIEB: Keys verschlüsselt (Fernet/AES-128) auf seinem Server. Vertraglich geregelt.
```
