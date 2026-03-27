"""
Datenbank — SQLite mit Write-Queue für sichere parallele Schreibzugriffe.
Alle Schreib-Operationen gehen über eine asyncio.Queue.
Ein Background-Task schreibt gebatcht alle 2 Sekunden.
"""

import asyncio
import sqlite3
import os
import json
from datetime import datetime, timedelta
from backend.config import DATABASE_PATH


class Database:
    def __init__(self):
        self._queue: asyncio.Queue = None
        self._running = False
        self._db_path = DATABASE_PATH

    async def init(self):
        """Datenbank initialisieren: Ordner, Tabellen, Write-Queue starten."""
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        self._create_tables()
        self._queue = asyncio.Queue()
        self._running = True
        asyncio.create_task(self._write_loop())

    def _get_conn(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _create_tables(self):
        conn = self._get_conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS api_keys (
                provider TEXT PRIMARY KEY,
                encrypted_key TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL DEFAULT 'info',
                message TEXT NOT NULL,
                automation_name TEXT
            );

            CREATE TABLE IF NOT EXISTS automation_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                automation_name TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                status TEXT NOT NULL DEFAULT 'running',
                result TEXT,
                error TEXT
            );

            CREATE TABLE IF NOT EXISTS automation_config (
                automation_name TEXT PRIMARY KEY,
                enabled INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                success INTEGER NOT NULL DEFAULT 0
            );
        """)
        conn.commit()
        conn.close()

    async def _write_loop(self):
        """Background-Task: sammelt Schreib-Operationen und führt sie alle 2 Sekunden gebatcht aus."""
        while self._running:
            await asyncio.sleep(2)
            batch = []
            while not self._queue.empty():
                try:
                    batch.append(self._queue.get_nowait())
                except asyncio.QueueEmpty:
                    break

            if not batch:
                continue

            conn = self._get_conn()
            try:
                for sql, params in batch:
                    conn.execute(sql, params)
                conn.commit()
            except Exception as e:
                print(f"FEHLER beim Schreiben in DB: {e}")
            finally:
                conn.close()

    async def enqueue(self, sql: str, params: tuple = ()):
        """Schreib-Operation in die Queue legen."""
        await self._queue.put((sql, params))

    # --- Logs ---

    async def save_log(self, message: str, level: str = "info", automation_name: str = None):
        await self.enqueue(
            "INSERT INTO logs (timestamp, level, message, automation_name) VALUES (?, ?, ?, ?)",
            (datetime.now().isoformat(), level, message, automation_name),
        )

    def get_logs(self, limit: int = 100, automation_name: str = None) -> list:
        conn = self._get_conn()
        if automation_name:
            rows = conn.execute(
                "SELECT * FROM logs WHERE automation_name = ? ORDER BY id DESC LIMIT ?",
                (automation_name, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM logs ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # --- API Keys ---

    async def save_api_key(self, provider: str, encrypted_key: str):
        await self.enqueue(
            "INSERT OR REPLACE INTO api_keys (provider, encrypted_key, updated_at) VALUES (?, ?, ?)",
            (provider, encrypted_key, datetime.now().isoformat()),
        )

    def get_api_key(self, provider: str) -> str | None:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT encrypted_key FROM api_keys WHERE provider = ?", (provider,)
        ).fetchone()
        conn.close()
        return row["encrypted_key"] if row else None

    def get_all_api_keys(self) -> list:
        conn = self._get_conn()
        rows = conn.execute("SELECT provider, encrypted_key, updated_at FROM api_keys").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # --- Automation Runs ---

    async def save_run(self, automation_name: str, status: str = "running") -> int:
        """Startet einen neuen Run und gibt die ID zurück."""
        conn = self._get_conn()
        cursor = conn.execute(
            "INSERT INTO automation_runs (automation_name, started_at, status) VALUES (?, ?, ?)",
            (automation_name, datetime.now().isoformat(), status),
        )
        run_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return run_id

    async def update_run(self, run_id: int, status: str, result: str = None, error: str = None):
        await self.enqueue(
            "UPDATE automation_runs SET finished_at = ?, status = ?, result = ?, error = ? WHERE id = ?",
            (datetime.now().isoformat(), status, result, error, run_id),
        )

    def get_runs(self, automation_name: str = None, limit: int = 10) -> list:
        conn = self._get_conn()
        if automation_name:
            rows = conn.execute(
                "SELECT * FROM automation_runs WHERE automation_name = ? ORDER BY id DESC LIMIT ?",
                (automation_name, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM automation_runs ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # --- Automation Config ---

    def is_automation_enabled(self, name: str) -> bool:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT enabled FROM automation_config WHERE automation_name = ?", (name,)
        ).fetchone()
        conn.close()
        if row is None:
            return True  # Standard: aktiviert
        return bool(row["enabled"])

    async def toggle_automation(self, name: str) -> bool:
        """Schaltet Automation um und gibt neuen Status zurück."""
        current = self.is_automation_enabled(name)
        new_state = 0 if current else 1
        conn = self._get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO automation_config (automation_name, enabled) VALUES (?, ?)",
            (name, new_state),
        )
        conn.commit()
        conn.close()
        return bool(new_state)

    # --- Login Attempts ---

    async def record_login_attempt(self, ip_address: str, success: bool):
        """Schreibt direkt (nicht über Queue), damit Rate-Limiting sofort greift."""
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO login_attempts (ip_address, timestamp, success) VALUES (?, ?, ?)",
            (ip_address, datetime.utcnow().isoformat(), int(success)),
        )
        conn.commit()
        conn.close()

    def get_recent_login_attempts(self, ip_address: str, minutes: int = 1) -> list:
        conn = self._get_conn()
        cutoff = (datetime.utcnow() - timedelta(minutes=minutes)).isoformat()
        rows = conn.execute(
            """SELECT * FROM login_attempts
               WHERE ip_address = ?
               AND timestamp > ?
               ORDER BY id DESC""",
            (ip_address, cutoff),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # --- Shutdown ---

    async def shutdown(self):
        """Write-Queue leeren und stoppen."""
        self._running = False
        # Restliche Queue-Einträge noch schreiben
        batch = []
        while not self._queue.empty():
            try:
                batch.append(self._queue.get_nowait())
            except asyncio.QueueEmpty:
                break
        if batch:
            conn = self._get_conn()
            for sql, params in batch:
                conn.execute(sql, params)
            conn.commit()
            conn.close()


# Globale Instanz
db = Database()
