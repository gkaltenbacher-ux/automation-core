"""
Scheduler — APScheduler liest Automationen aus client.json
und registriert Cron-Jobs basierend auf dem "schedule"-Feld.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.pipeline import get_client_config, run_automation
from backend.logger import log


scheduler = AsyncIOScheduler()


async def start_scheduler():
    """Liest client.json und registriert alle Automationen als Cron-Jobs."""
    config = get_client_config()

    for automation in config.get("automations", []):
        name = automation["name"]
        schedule = automation.get("schedule", "")
        enabled = automation.get("enabled", True)

        if not schedule or not enabled:
            continue

        try:
            # Cron-Ausdruck parsen (z.B. "*/10 * * * *")
            parts = schedule.split()
            if len(parts) == 5:
                trigger = CronTrigger(
                    minute=parts[0],
                    hour=parts[1],
                    day=parts[2],
                    month=parts[3],
                    day_of_week=parts[4],
                )
            else:
                await log(f"Ungültiger Schedule für '{name}': {schedule}", "error", name)
                continue

            scheduler.add_job(
                run_automation,
                trigger=trigger,
                args=[name],
                id=name,
                replace_existing=True,
                name=name,
            )
            await log(f"Automation '{name}' geplant: {schedule}", "info", name)

        except Exception as e:
            await log(f"Fehler beim Planen von '{name}': {e}", "error", name)

    scheduler.start()
    await log("Scheduler gestartet.")


async def stop_scheduler():
    """Scheduler sauber beenden."""
    scheduler.shutdown(wait=False)
    await log("Scheduler gestoppt.")


def reschedule_automation(name: str, enabled: bool):
    """Pausiert oder reaktiviert einen Job im Scheduler."""
    if enabled:
        scheduler.resume_job(name)
    else:
        scheduler.pause_job(name)
