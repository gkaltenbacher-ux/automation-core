# Blueprint: Lead-Generierung

Lead-Scraping + Bewertung + Personalisierte E-Mails + CRM (Notion).

## Was enthalten ist

**3 Agents:**
- lead_researcher — Google Maps + LinkedIn Scraping, E-Mail-Extraktion, Scoring
- outreach_agent — E-Mail-Generierung + Versand
- crm_agent — Notion CRM Management

**1 Workflow:**
- Lead-Scraping: Scrapen → Pause → E-Mails generieren → Pause → Versenden

**5 Prompt-Templates:**
- Lead-Profil-Analyse
- Lead-Scoring
- Erste Kontakt-Nachricht
- Follow-Up Nachricht
- Quick-Win Analyse

## Benoetigte API-Keys

- OpenAI (Orchestrator + Agents)
- Apify (Google Maps + LinkedIn + Email Scraping)
- Notion (CRM)
- Gmail (E-Mail-Versand)
- Telegram (optional, fuer Remote-Steuerung)

## Geschaetzte Kosten

- Setup: 1-2 Stunden
- Monatlich: CHF 20-50 (je nach Volumen)
- Apify: ~$2/1000 Google Maps Results
- OpenAI: ~$0.01/Lead (Scoring + E-Mail)

## Anpassen

1. `client.json` oeffnen
2. `company_name` aendern
3. Agent System-Prompts an Kundenbranche anpassen
4. Prompt-Templates in `custom_prompts/` anpassen
5. Fertig
