"""
Workflow Engine — fuehrt sequenzielle Workflows aus.

Step-Typen:
  - "agent": Ruft einen Agent auf
  - "tool": Ruft ein Tool direkt auf
  - "pause": Pausiert fuer Bestaetigung (Dashboard/Telegram)

State wird in SQLite gespeichert → ueberlebt Server-Restart.
Workflows werden in client.json definiert.
"""
import json
import logging
import secrets
import sqlite3
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class WorkflowEngine:
    def __init__(self, agent_registry: dict, tool_registry: dict, context: dict, data_dir: str = None):
        data_dir = Path(data_dir) if data_dir else Path(os.environ.get("DATA_DIR", "data"))
        data_dir.mkdir(parents=True, exist_ok=True)
        self._db_path = data_dir / "workflows.db"
        self.agents = agent_registry
        self.tools = tool_registry
        self.context = context
        self._init_db()

    def _init_db(self):
        conn = self._get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workflow_runs (
                id TEXT PRIMARY KEY,
                workflow_name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'running',
                current_step INTEGER DEFAULT 0,
                state_json TEXT DEFAULT '{}',
                started_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                error TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _get_db(self):
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        return conn

    async def start(self, workflow_def: dict, initial_data: dict = None) -> str:
        """Startet einen Workflow und fuehrt Steps aus bis Pause oder Ende."""
        run_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(3)}"
        state = initial_data or {}
        now = datetime.now().isoformat()

        conn = self._get_db()
        conn.execute(
            "INSERT INTO workflow_runs (id, workflow_name, status, current_step, state_json, started_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (run_id, workflow_def["name"], "running", 0, json.dumps(state, default=str), now, now),
        )
        conn.commit()
        conn.close()

        log = self.context.get("log")
        if log:
            await log(f"Workflow '{workflow_def['name']}' gestartet ({run_id})")

        await self._execute_from(run_id, workflow_def, 0, state)
        return run_id

    async def resume(self, run_id: str, workflow_def: dict) -> str:
        """Setzt einen pausierten Workflow fort."""
        conn = self._get_db()
        row = conn.execute("SELECT * FROM workflow_runs WHERE id = ?", (run_id,)).fetchone()
        conn.close()

        if not row:
            return "Workflow nicht gefunden"
        if row["status"] != "paused":
            return f"Workflow ist nicht pausiert (Status: {row['status']})"

        state = json.loads(row["state_json"])
        next_step = row["current_step"] + 1

        log = self.context.get("log")
        if log:
            await log(f"Workflow '{row['workflow_name']}' fortgesetzt ab Schritt {next_step + 1}")

        self._update_run(run_id, status="running")
        await self._execute_from(run_id, workflow_def, next_step, state)
        return "Fortgesetzt"

    async def _execute_from(self, run_id: str, workflow_def: dict, start_step: int, state: dict):
        """Fuehrt Steps ab start_step aus."""
        steps = workflow_def.get("steps", [])
        log = self.context.get("log")

        for i in range(start_step, len(steps)):
            step = steps[i]
            step_type = step.get("type", "agent")

            if log:
                await log(f"Schritt {i + 1}/{len(steps)}: {step_type} — {step.get('agent', step.get('tool', step.get('message', '')))}")

            try:
                if step_type == "agent":
                    agent = self.agents.get(step["agent"])
                    if not agent:
                        raise ValueError(f"Agent '{step['agent']}' nicht gefunden")
                    result = await agent.execute({"task": step.get("task", ""), "data": state})
                    if step.get("data_key"):
                        state[step["data_key"]] = result.get("data", result)

                elif step_type == "tool":
                    tool = self.tools.get(step["tool"])
                    if not tool:
                        raise ValueError(f"Tool '{step['tool']}' nicht gefunden")
                    result = await tool["run"](step.get("params", {}), self.context)
                    if step.get("data_key"):
                        state[step["data_key"]] = result.get("data", result)

                elif step_type == "pause":
                    message = step.get("message", "Warte auf Bestaetigung")
                    # Variablen in Message ersetzen
                    try:
                        message = message.format(**state)
                    except (KeyError, IndexError):
                        pass
                    self._update_run(run_id, status="paused", step=i, state=state)
                    if log:
                        await log(f"Workflow pausiert: {message}")
                    return  # Hier aufhoeren, resume() macht weiter

                self._update_run(run_id, step=i, state=state)

            except Exception as e:
                logger.error(f"Workflow {run_id} Schritt {i} Fehler: {e}")
                self._update_run(run_id, status="error", step=i, state=state, error=str(e))
                if log:
                    await log(f"Workflow Fehler in Schritt {i + 1}: {e}", "error")
                return

        # Alle Steps fertig
        self._update_run(run_id, status="completed", state=state)
        if log:
            await log(f"Workflow '{workflow_def['name']}' abgeschlossen")

    def _update_run(self, run_id: str, status: str = None, step: int = None, state: dict = None, error: str = None):
        conn = self._get_db()
        updates = ["updated_at = ?"]
        params = [datetime.now().isoformat()]

        if status:
            updates.append("status = ?")
            params.append(status)
        if step is not None:
            updates.append("current_step = ?")
            params.append(step)
        if state is not None:
            updates.append("state_json = ?")
            params.append(json.dumps(state, default=str))
        if error:
            updates.append("error = ?")
            params.append(error)

        params.append(run_id)
        conn.execute(f"UPDATE workflow_runs SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
        conn.close()

    def get_status(self, run_id: str) -> dict | None:
        conn = self._get_db()
        row = conn.execute("SELECT * FROM workflow_runs WHERE id = ?", (run_id,)).fetchone()
        conn.close()
        if not row:
            return None
        return {
            "id": row["id"],
            "workflow_name": row["workflow_name"],
            "status": row["status"],
            "current_step": row["current_step"],
            "state": json.loads(row["state_json"]),
            "started_at": row["started_at"],
            "updated_at": row["updated_at"],
            "error": row["error"],
        }

    def list_runs(self, workflow_name: str = None, limit: int = 20) -> list:
        conn = self._get_db()
        if workflow_name:
            rows = conn.execute(
                "SELECT id, workflow_name, status, current_step, started_at, updated_at, error FROM workflow_runs WHERE workflow_name = ? ORDER BY started_at DESC LIMIT ?",
                (workflow_name, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, workflow_name, status, current_step, started_at, updated_at, error FROM workflow_runs ORDER BY started_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
