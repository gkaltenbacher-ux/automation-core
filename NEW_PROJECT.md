# Neues Kundenprojekt starten

## Ablauf (immer gleich)

### 1. Repo erstellen
```bash
mkdir kunde-NAME-PROJEKT
cd kunde-NAME-PROJEKT
git init
```

### 2. Core kopieren
```bash
# Alles ausser blueprints und .git kopieren
cp -r /pfad/zu/automation-core/backend/ ./core/backend/
cp -r /pfad/zu/automation-core/dashboard/ ./core/dashboard/
cp /pfad/zu/automation-core/Dockerfile ./
cp /pfad/zu/automation-core/docker-compose.yml ./
cp /pfad/zu/automation-core/requirements.txt ./
cp /pfad/zu/automation-core/.env.example ./.env
```

### 3. Blueprint waehlen
```bash
# Beispiel: Lead-Generierung
cp -r /pfad/zu/automation-core/blueprints/lead_generation/client.json ./config/client.json
cp -r /pfad/zu/automation-core/blueprints/lead_generation/custom_prompts/ ./config/custom_prompts/
```

### 4. Blocks verlinken
```bash
ln -sf /pfad/zu/automation-blocks ./blocks
```

### 5. Agents + Tools erstellen
```bash
mkdir -p agents tools
# Agents und Tools aus dem Blueprint ins Projekt kopieren
# oder neue erstellen
```

### 6. Anpassen
- `config/client.json`: company_name, Prompts, Agents anpassen
- `config/custom_prompts/`: E-Mail-Vorlagen anpassen
- `.env`: DASHBOARD_PASSWORD setzen

### 7. Testen
```bash
docker compose up
# Browser: http://localhost:8000
```

### 8. Deployen
```bash
git add . && git commit -m "Initial setup"
git push
# Coolify: Neues Projekt, Repo verbinden, deployen
```

### 9. Lernen
Nach dem Projekt:
- system_memory.json aktualisieren
- Wenn neuer Projekttyp: als Blueprint speichern
- Neue Tools/Agents in Libraries aktualisieren

## Verfuegbare Blueprints

- `lead_generation/` — Lead-Scraping + Bewertung + E-Mail Outreach + CRM
- (weitere folgen mit jedem neuen Kundenprojekt)
