"""
DSGVO-Modul — Datenschutz-Grundverordnung Compliance.

Funktionen:
- Consent-Logging: Was wurde wann warum gesammelt
- Daten-Export: Alle Daten einer Person als JSON (Art. 15)
- Daten-Loeschung: Alle Daten einer Person loeschen (Art. 17)
- Audit-Trail: Wer hat wann auf was zugegriffen
- Externe Hinweise: Was muss manuell geloescht werden (Notion, Gmail, etc.)

Nutzung ueber context["dsgvo"]:
    await context["dsgvo"].log_data_collection(
        actor="lead_researcher",
        person_id="max@example.com",
        category="lead_data",
        source="google_maps_scraping",
    )
"""
import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path


DATA_DIR = Path(os.environ.get("DATA_DIR", "data"))


class DSGVOManager:
    def __init__(self, data_dir: str = None, config: dict = None):
        """
        Args:
            data_dir: Verzeichnis fuer die Datenbank
            config: DSGVO-Config aus client.json
        """
        self._data_dir = Path(data_dir) if data_dir else DATA_DIR
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._db_path = self._data_dir / "dsgvo.db"
        self._config = config or {}
        self._init_db()

    def _init_db(self):
        conn = self._get_db()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS dsgvo_consent (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_identifier TEXT NOT NULL,
                data_category TEXT NOT NULL,
                purpose TEXT NOT NULL,
                source TEXT NOT NULL,
                consent_type TEXT NOT NULL,
                granted_at TEXT NOT NULL,
                revoked_at TEXT,
                notes TEXT
            );

            CREATE TABLE IF NOT EXISTS dsgvo_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                person_identifier TEXT,
                data_category TEXT,
                details TEXT
            );

            CREATE TABLE IF NOT EXISTS dsgvo_data_inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_identifier TEXT NOT NULL,
                data_category TEXT NOT NULL,
                data_location TEXT NOT NULL,
                collected_at TEXT NOT NULL,
                notes TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_consent_person ON dsgvo_consent(person_identifier);
            CREATE INDEX IF NOT EXISTS idx_audit_person ON dsgvo_audit(person_identifier);
            CREATE INDEX IF NOT EXISTS idx_inventory_person ON dsgvo_data_inventory(person_identifier);
        """)
        conn.commit()
        conn.close()

    def _get_db(self):
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        return conn

    # === CONSENT ===

    async def log_consent(
        self,
        person_id: str,
        category: str,
        purpose: str,
        source: str,
        consent_type: str = "legitimate_interest",
        notes: str = None,
    ):
        """Loggt eine Einwilligung/Rechtsgrundlage fuer Datenverarbeitung."""
        conn = self._get_db()
        conn.execute(
            """INSERT INTO dsgvo_consent
               (person_identifier, data_category, purpose, source, consent_type, granted_at, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (person_id, category, purpose, source, consent_type, datetime.now().isoformat(), notes),
        )
        conn.commit()
        conn.close()

    async def revoke_consent(self, person_id: str, category: str = None):
        """Widerruft Einwilligung — spezifisch oder alle."""
        conn = self._get_db()
        now = datetime.now().isoformat()
        if category:
            conn.execute(
                "UPDATE dsgvo_consent SET revoked_at = ? WHERE person_identifier = ? AND data_category = ? AND revoked_at IS NULL",
                (now, person_id, category),
            )
        else:
            conn.execute(
                "UPDATE dsgvo_consent SET revoked_at = ? WHERE person_identifier = ? AND revoked_at IS NULL",
                (now, person_id),
            )
        conn.commit()
        conn.close()

        await self._log_audit("system", "consent_revoked", person_id, category)

    async def get_consents(self, person_id: str = None, active_only: bool = True) -> list:
        conn = self._get_db()
        if person_id:
            if active_only:
                rows = conn.execute(
                    "SELECT * FROM dsgvo_consent WHERE person_identifier = ? AND revoked_at IS NULL ORDER BY granted_at DESC",
                    (person_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM dsgvo_consent WHERE person_identifier = ? ORDER BY granted_at DESC",
                    (person_id,),
                ).fetchall()
        else:
            if active_only:
                rows = conn.execute(
                    "SELECT * FROM dsgvo_consent WHERE revoked_at IS NULL ORDER BY granted_at DESC"
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM dsgvo_consent ORDER BY granted_at DESC"
                ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # === DATA COLLECTION LOGGING ===

    async def log_data_collection(
        self,
        actor: str,
        person_id: str,
        category: str,
        source: str,
        data_location: str = "sqlite",
        details: str = None,
    ):
        """Loggt dass Daten ueber eine Person gesammelt wurden.

        Sollte von jedem Tool/Agent aufgerufen werden der Personendaten verarbeitet.
        """
        conn = self._get_db()

        # Data Inventory aktualisieren
        conn.execute(
            """INSERT INTO dsgvo_data_inventory
               (person_identifier, data_category, data_location, collected_at, notes)
               VALUES (?, ?, ?, ?, ?)""",
            (person_id, category, data_location, datetime.now().isoformat(), details),
        )

        conn.commit()
        conn.close()

        await self._log_audit(actor, "data_collected", person_id, category, details)

    async def log_data_access(self, actor: str, person_id: str, category: str = None, details: str = None):
        """Loggt Zugriff auf Personendaten."""
        await self._log_audit(actor, "data_accessed", person_id, category, details)

    # === DATEN-EXPORT (Art. 15 DSGVO) ===

    async def export_person_data(self, person_id: str) -> dict:
        """Exportiert ALLE gespeicherten Daten ueber eine Person.

        Returns:
            {
                "person_identifier": "...",
                "exported_at": "...",
                "consents": [...],
                "data_inventory": [...],
                "audit_trail": [...]
            }
        """
        conn = self._get_db()

        consents = [dict(r) for r in conn.execute(
            "SELECT * FROM dsgvo_consent WHERE person_identifier = ?", (person_id,)
        ).fetchall()]

        inventory = [dict(r) for r in conn.execute(
            "SELECT * FROM dsgvo_data_inventory WHERE person_identifier = ?", (person_id,)
        ).fetchall()]

        audit = [dict(r) for r in conn.execute(
            "SELECT * FROM dsgvo_audit WHERE person_identifier = ? ORDER BY timestamp DESC", (person_id,)
        ).fetchall()]

        conn.close()

        await self._log_audit("dashboard_user", "data_exported", person_id)

        return {
            "person_identifier": person_id,
            "exported_at": datetime.now().isoformat(),
            "consents": consents,
            "data_inventory": inventory,
            "audit_trail": audit,
        }

    # === DATEN-LOESCHUNG (Art. 17 DSGVO) ===

    async def delete_person_data(self, person_id: str) -> dict:
        """Loescht ALLE Daten ueber eine Person aus dem System.

        Externe Systeme (Notion, Gmail) werden NICHT automatisch geloescht —
        stattdessen wird eine Liste zurueckgegeben was manuell geloescht werden muss.
        """
        conn = self._get_db()

        # Inventar pruefen — was liegt wo?
        inventory = [dict(r) for r in conn.execute(
            "SELECT DISTINCT data_location, data_category FROM dsgvo_data_inventory WHERE person_identifier = ?",
            (person_id,),
        ).fetchall()]

        # Externe Loeschungen identifizieren
        external_deletions = []
        for item in inventory:
            location = item["data_location"]
            if location not in ("sqlite", "local"):
                external_deletions.append({
                    "location": location,
                    "category": item["data_category"],
                    "action": f"Manuell loeschen: {item['data_category']} in {location}",
                })

        # Lokale Daten loeschen
        deleted = {
            "consents": conn.execute(
                "DELETE FROM dsgvo_consent WHERE person_identifier = ?", (person_id,)
            ).rowcount,
            "data_inventory": conn.execute(
                "DELETE FROM dsgvo_data_inventory WHERE person_identifier = ?", (person_id,)
            ).rowcount,
        }

        conn.commit()
        conn.close()

        # Meta-Audit: Loeschung selbst loggen
        await self._log_audit(
            "dashboard_user", "data_deleted", person_id, None,
            json.dumps({"deleted": deleted, "external_pending": len(external_deletions)}, ensure_ascii=False),
        )

        return {
            "person_identifier": person_id,
            "deleted_at": datetime.now().isoformat(),
            "deleted_records": deleted,
            "external_deletions_required": external_deletions,
        }

    # === AUDIT TRAIL ===

    async def _log_audit(
        self,
        actor: str,
        action: str,
        person_id: str = None,
        category: str = None,
        details: str = None,
    ):
        conn = self._get_db()
        conn.execute(
            """INSERT INTO dsgvo_audit (timestamp, actor, action, person_identifier, data_category, details)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (datetime.now().isoformat(), actor, action, person_id, category, details),
        )
        conn.commit()
        conn.close()

    async def get_audit_trail(self, person_id: str = None, limit: int = 100) -> list:
        conn = self._get_db()
        if person_id:
            rows = conn.execute(
                "SELECT * FROM dsgvo_audit WHERE person_identifier = ? ORDER BY timestamp DESC LIMIT ?",
                (person_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM dsgvo_audit ORDER BY timestamp DESC LIMIT ?", (limit,),
            ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # === PERSONEN-UEBERSICHT ===

    async def list_persons(self, limit: int = 100) -> list:
        """Gibt alle bekannten Personen zurueck mit Anzahl Datensaetze."""
        conn = self._get_db()
        rows = conn.execute(
            """SELECT person_identifier,
                      COUNT(*) as record_count,
                      MIN(collected_at) as first_collected,
                      MAX(collected_at) as last_collected
               FROM dsgvo_data_inventory
               GROUP BY person_identifier
               ORDER BY last_collected DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]


def create_dsgvo_manager(config: dict, data_dir: str = None) -> DSGVOManager:
    """Factory: Erstellt DSGVOManager aus client.json Config."""
    dsgvo_config = config.get("dsgvo", {})
    if not dsgvo_config.get("enabled", True):
        return None
    return DSGVOManager(data_dir=data_dir, config=dsgvo_config)
