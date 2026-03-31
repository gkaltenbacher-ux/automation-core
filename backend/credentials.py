"""
Credential Management — zentrale Verwaltung aller API-Keys, Bot-Tokens, Webhook-Secrets.
Verschlüsselt in SQLite, überlebt Redeploys (Persistent Volume).

Credential-Typen werden aus client.json geladen — nicht hardcoded.
Built-in Test-Funktionen für gängige Provider (OpenAI, Telegram, Apify, Notion, Gmail).
"""
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from cryptography.fernet import Fernet

import httpx


DATA_DIR = Path(os.environ.get("DATA_DIR", "data"))


class CredentialManager:
    def __init__(self, data_dir: str = None, credential_types: dict = None, key_mapping: dict = None):
        """
        Args:
            data_dir: Verzeichnis für credentials.db + encryption.key
            credential_types: Schema aus client.json (welche Credential-Typen es gibt)
            key_mapping: Mapping für get_api_key() Bridge aus client.json
        """
        self._data_dir = Path(data_dir) if data_dir else DATA_DIR
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._db_path = self._data_dir / "credentials.db"
        self._key_path = self._data_dir / "encryption.key"
        self._credential_types = credential_types or {}
        self._key_mapping = key_mapping or {}
        self._fernet = None
        self._init()

    def _init(self):
        if self._key_path.exists():
            key = self._key_path.read_bytes().strip()
        else:
            key = Fernet.generate_key()
            self._key_path.write_bytes(key)
            try:
                self._key_path.chmod(0o600)
            except OSError:
                pass

        self._fernet = Fernet(key)

        with self._get_db() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS credentials (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    encrypted_data BLOB NOT NULL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now'))
                )
            """)

    def _get_db(self):
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _encrypt(self, data: dict) -> bytes:
        return self._fernet.encrypt(json.dumps(data).encode("utf-8"))

    def _decrypt(self, encrypted: bytes) -> dict:
        return json.loads(self._fernet.decrypt(encrypted).decode("utf-8"))

    # === Credential-Typen (aus Config) ===

    def get_credential_types(self) -> dict:
        return self._credential_types

    def set_credential_types(self, types: dict):
        self._credential_types = types

    def set_key_mapping(self, mapping: dict):
        self._key_mapping = mapping

    # === CRUD ===

    def create(self, name: str, cred_type: str, data: dict) -> str:
        cred_id = f"cred_{cred_type}_{int(datetime.now().timestamp())}"
        with self._get_db() as conn:
            conn.execute(
                """INSERT INTO credentials (id, name, type, encrypted_data)
                   VALUES (?, ?, ?, ?)""",
                (cred_id, name, cred_type, self._encrypt(data)),
            )
        return cred_id

    def get(self, cred_id: str) -> dict | None:
        with self._get_db() as conn:
            row = conn.execute("SELECT * FROM credentials WHERE id = ?", (cred_id,)).fetchone()
        if not row:
            return None
        return {
            "id": row["id"], "name": row["name"], "type": row["type"],
            "data": self._decrypt(row["encrypted_data"]),
            "status": row["status"],
            "created_at": row["created_at"], "updated_at": row["updated_at"],
        }

    def get_by_type(self, cred_type: str) -> dict | None:
        """Gibt das erste aktive Credential eines Typs zurück."""
        with self._get_db() as conn:
            row = conn.execute(
                "SELECT * FROM credentials WHERE type = ? AND status = 'active' ORDER BY updated_at DESC LIMIT 1",
                (cred_type,),
            ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"], "name": row["name"], "type": row["type"],
            "data": self._decrypt(row["encrypted_data"]),
            "status": row["status"],
        }

    def list_all(self) -> list:
        with self._get_db() as conn:
            rows = conn.execute(
                "SELECT id, name, type, status, created_at, updated_at FROM credentials ORDER BY type, name"
            ).fetchall()
        result = []
        for row in rows:
            type_def = self._credential_types.get(row["type"], {})
            result.append({
                "id": row["id"], "name": row["name"], "type": row["type"],
                "type_name": type_def.get("name", row["type"]),
                "icon": type_def.get("icon", ""),
                "status": row["status"],
                "created_at": row["created_at"], "updated_at": row["updated_at"],
            })
        return result

    def update(self, cred_id: str, data: dict):
        with self._get_db() as conn:
            conn.execute(
                "UPDATE credentials SET encrypted_data = ?, updated_at = datetime('now') WHERE id = ?",
                (self._encrypt(data), cred_id),
            )

    def delete(self, cred_id: str):
        with self._get_db() as conn:
            conn.execute("DELETE FROM credentials WHERE id = ?", (cred_id,))

    # === BRIDGE zu context["get_api_key"] ===

    def get_api_key(self, service: str) -> str:
        """Kompatibilitäts-Bridge: Blocks/Tools rufen context["get_api_key"]("apify") auf.

        Mapping kommt aus client.json:
        "key_mapping": {
            "apify": {"credential_type": "apify_api", "field": "api_token"},
            "openai": {"credential_type": "openai_api", "field": "api_key"}
        }
        """
        if service not in self._key_mapping:
            raise KeyError(f"Unbekannter Service: {service}. Nicht in key_mapping konfiguriert.")

        mapping = self._key_mapping[service]
        cred_type = mapping["credential_type"]
        field_name = mapping["field"]

        cred = self.get_by_type(cred_type)
        if not cred:
            raise KeyError(
                f"Kein Credential für '{service}' gefunden. "
                f"Bitte im Dashboard unter Credentials eintragen."
            )

        value = cred["data"].get(field_name, "")
        if not value:
            raise KeyError(f"Feld '{field_name}' ist leer im Credential '{cred['name']}'")

        return value

    # === TESTS ===

    async def test(self, cred_id: str) -> dict:
        cred = self.get(cred_id)
        if not cred:
            return {"ok": False, "error": "Credential nicht gefunden"}

        type_def = self._credential_types.get(cred["type"], {})
        test_fn_name = type_def.get("test_fn")
        if not test_fn_name:
            return {"ok": True, "message": "Gespeichert (kein automatischer Test verfügbar)"}

        test_fn = BUILTIN_TESTERS.get(test_fn_name)
        if not test_fn:
            return {"ok": True, "message": "Gespeichert"}

        return await test_fn(cred["data"])


# === BUILT-IN TEST-FUNKTIONEN ===

async def _test_openai(data: dict) -> dict:
    key = data.get("api_key", "")
    if not key:
        return {"ok": False, "error": "API Key fehlt"}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {key}"},
        )
        if resp.status_code == 200:
            return {"ok": True, "message": "API Key gueltig"}
        return {"ok": False, "error": f"Ungueltiger Key ({resp.status_code})"}


async def _test_telegram(data: dict) -> dict:
    token = data.get("bot_token", "")
    if not token:
        return {"ok": False, "error": "Bot Token fehlt"}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"https://api.telegram.org/bot{token}/getMe")
        if resp.status_code == 200:
            bot = resp.json()["result"]
            return {"ok": True, "message": f"Verbunden mit @{bot['username']}"}
        return {"ok": False, "error": f"Ungueltiger Token ({resp.status_code})"}


async def _test_apify(data: dict) -> dict:
    token = data.get("api_token", "")
    if not token:
        return {"ok": False, "error": "API Token fehlt"}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get("https://api.apify.com/v2/users/me", params={"token": token})
        if resp.status_code == 200:
            user = resp.json()["data"]
            return {"ok": True, "message": f"Verbunden als {user.get('username', 'OK')}"}
        return {"ok": False, "error": f"Ungueltiger Token ({resp.status_code})"}


async def _test_notion(data: dict) -> dict:
    key = data.get("api_key", "")
    if not key:
        return {"ok": False, "error": "Integration Token fehlt"}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            "https://api.notion.com/v1/users/me",
            headers={"Authorization": f"Bearer {key}", "Notion-Version": "2022-06-28"},
        )
        if resp.status_code == 200:
            return {"ok": True, "message": "Notion verbunden"}
        return {"ok": False, "error": f"Ungueltiger Token ({resp.status_code})"}


async def _test_gmail(data: dict) -> dict:
    email = data.get("email", "")
    password = data.get("app_password", "")
    if not email or not password:
        return {"ok": False, "error": "E-Mail oder App-Password fehlt"}
    try:
        import smtplib
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10)
        server.login(email, password)
        server.quit()
        return {"ok": True, "message": f"Gmail verbunden ({email})"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


BUILTIN_TESTERS = {
    "openai": _test_openai,
    "telegram": _test_telegram,
    "apify": _test_apify,
    "notion": _test_notion,
    "gmail": _test_gmail,
}


def create_credential_manager(config: dict, data_dir: str = None) -> CredentialManager:
    """Factory: Erstellt CredentialManager mit Typen und Mapping aus client.json.

    Erwartet in config:
        "credential_types": { "openai_api": { "name": "OpenAI", "fields": [...], "test_fn": "openai" }, ... }
        "key_mapping": { "openai": { "credential_type": "openai_api", "field": "api_key" }, ... }
    """
    return CredentialManager(
        data_dir=data_dir,
        credential_types=config.get("credential_types", {}),
        key_mapping=config.get("key_mapping", {}),
    )


def create_get_api_key(credential_manager: CredentialManager):
    """Factory: Gibt async get_api_key Funktion zurück für context["get_api_key"]."""
    async def get_api_key(service: str) -> str:
        return credential_manager.get_api_key(service)

    return get_api_key
