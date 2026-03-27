"""
Pipeline-Engine — liest client.json, importiert Blocks, führt sie der Reihe nach aus.
Ausgabe Block N = Eingabe Block N+1.
Bei Fehler: 3 Retries mit steigender Wartezeit.
"""

import asyncio
import importlib
import json
import os
import sys
from backend.database import db
from backend.crypto import get_api_key
from backend.logger import log


CLIENT_CONFIG_PATH = os.getenv("CLIENT_CONFIG_PATH", "config/client.json")
BLOCKS_PATH = os.getenv("BLOCKS_PATH", "blocks")


def _load_client_config() -> dict:
    """Lädt die client.json."""
    if not os.path.exists(CLIENT_CONFIG_PATH):
        return {"automations": [], "api_keys_needed": []}
    with open(CLIENT_CONFIG_PATH, "r") as f:
        return json.load(f)


def _import_block(block_name: str):
    """Importiert einen Block aus dem blocks/ Ordner."""
    # blocks/ zum Pfad hinzufügen falls nötig
    blocks_dir = os.path.abspath(BLOCKS_PATH)
    if blocks_dir not in sys.path:
        sys.path.insert(0, blocks_dir)

    # Modul importieren (oder neu laden falls schon importiert)
    if block_name in sys.modules:
        return importlib.reload(sys.modules[block_name])
    return importlib.import_module(block_name)


async def run_automation(automation_name: str):
    """Führt eine komplette Automation aus client.json aus."""
    config = _load_client_config()

    # Automation finden
    automation = None
    for a in config.get("automations", []):
        if a["name"] == automation_name:
            automation = a
            break

    if not automation:
        await log(f"Automation '{automation_name}' nicht gefunden.", "error")
        return

    # Prüfen ob aktiviert
    if not db.is_automation_enabled(automation_name):
        await log(f"Automation '{automation_name}' ist deaktiviert.", "info", automation_name)
        return

    # Run starten
    run_id = await db.save_run(automation_name, "running")
    await log(f"Automation gestartet.", "info", automation_name)

    # Context für die Blocks
    context = {
        "log": lambda msg, level="info": log(msg, level, automation_name),
        "get_api_key": get_api_key,
        "db": db,
    }

    input_data = {}
    steps = automation.get("steps", [])

    for i, step in enumerate(steps):
        block_name = step["block"]
        block_config = step.get("config", {})
        step_label = f"Schritt {i + 1}/{len(steps)}: {block_name}"

        # Retry-Logik: 3 Versuche mit steigender Wartezeit
        success = False
        last_error = None

        for attempt in range(1, 4):
            try:
                block_module = _import_block(block_name)
                await log(f"{step_label} wird ausgeführt...", "info", automation_name)

                result = await block_module.execute(input_data, block_config, context)

                if result.get("success"):
                    input_data = result.get("data", {})
                    await log(f"{step_label} erfolgreich.", "info", automation_name)
                    success = True
                    break
                else:
                    last_error = result.get("error", "Unbekannter Fehler")
                    await log(
                        f"{step_label} fehlgeschlagen (Versuch {attempt}/3): {last_error}",
                        "warning", automation_name,
                    )
            except Exception as e:
                last_error = str(e)
                await log(
                    f"{step_label} Fehler (Versuch {attempt}/3): {last_error}",
                    "error", automation_name,
                )

            if attempt < 3:
                wait = attempt * 5  # 5s, 10s
                await log(f"Warte {wait} Sekunden vor erneutem Versuch...", "info", automation_name)
                await asyncio.sleep(wait)

        if not success:
            await log(
                f"Automation abgebrochen nach 3 Versuchen bei {step_label}: {last_error}",
                "error", automation_name,
            )
            await db.update_run(run_id, "error", error=last_error)
            return

    # Alles erfolgreich
    await log(f"Automation erfolgreich abgeschlossen.", "info", automation_name)
    result_str = json.dumps(input_data, ensure_ascii=False, default=str)
    await db.update_run(run_id, "success", result=result_str)


def get_all_automations() -> list:
    """Gibt alle Automationen aus client.json mit Status zurück."""
    config = _load_client_config()
    automations = []
    for a in config.get("automations", []):
        name = a["name"]
        automations.append({
            "name": name,
            "description": a.get("description", ""),
            "schedule": a.get("schedule", ""),
            "enabled": db.is_automation_enabled(name),
            "steps": [s["block"] for s in a.get("steps", [])],
        })
    return automations


async def toggle_automation(name: str) -> bool:
    """Schaltet eine Automation an/aus. Gibt neuen Status zurück."""
    new_state = await db.toggle_automation(name)
    status = "aktiviert" if new_state else "deaktiviert"
    await log(f"Automation '{name}' {status}.", "info", name)
    return new_state


def get_client_config() -> dict:
    """Gibt die gesamte client.json zurück (für Dashboard)."""
    return _load_client_config()
