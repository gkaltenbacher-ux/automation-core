"""
Cost Tracker — zaehlt Tokens und Kosten pro LLM-Call.

Wird automatisch von BaseAgent.call_llm() aufgerufen.
Speichert in eigener SQLite-Tabelle, zeigt Zusammenfassungen.
"""
import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path


# Preise pro 1M Tokens (USD) — Stand Maerz 2026
MODEL_PRICES = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4.1-mini": {"input": 0.40, "output": 1.60},
    "gpt-4.1": {"input": 2.00, "output": 8.00},
}


class CostTracker:
    def __init__(self, data_dir: str = None):
        data_dir = Path(data_dir) if data_dir else Path(os.environ.get("DATA_DIR", "data"))
        data_dir.mkdir(parents=True, exist_ok=True)
        self._db_path = data_dir / "costs.db"
        self._init_db()

    def _init_db(self):
        conn = self._get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cost_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                model TEXT NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL,
                cost_usd REAL NOT NULL,
                agent_name TEXT,
                workflow_run_id TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _get_db(self):
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _calc_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        prices = MODEL_PRICES.get(model, MODEL_PRICES["gpt-4o-mini"])
        return (input_tokens * prices["input"] + output_tokens * prices["output"]) / 1_000_000

    async def track_llm_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        agent_name: str = None,
        workflow_run_id: str = None,
    ):
        """Loggt einen LLM-Call mit Tokens und Kosten."""
        cost = self._calc_cost(model, input_tokens, output_tokens)
        conn = self._get_db()
        conn.execute(
            """INSERT INTO cost_log (timestamp, model, input_tokens, output_tokens, cost_usd, agent_name, workflow_run_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (datetime.now().isoformat(), model, input_tokens, output_tokens, cost, agent_name, workflow_run_id),
        )
        conn.commit()
        conn.close()

    def get_summary(self, period: str = "today") -> dict:
        """Zusammenfassung: total_cost, total_tokens, calls, by_agent.

        period: "today", "week", "month"
        """
        cutoff = self._period_cutoff(period)
        conn = self._get_db()

        # Gesamt
        row = conn.execute(
            """SELECT COALESCE(SUM(cost_usd), 0) as total_cost,
                      COALESCE(SUM(input_tokens + output_tokens), 0) as total_tokens,
                      COUNT(*) as calls
               FROM cost_log WHERE timestamp >= ?""",
            (cutoff,),
        ).fetchone()

        # Pro Agent
        agent_rows = conn.execute(
            """SELECT agent_name, SUM(cost_usd) as cost, SUM(input_tokens + output_tokens) as tokens, COUNT(*) as calls
               FROM cost_log WHERE timestamp >= ? AND agent_name IS NOT NULL
               GROUP BY agent_name ORDER BY cost DESC""",
            (cutoff,),
        ).fetchall()

        conn.close()

        return {
            "period": period,
            "total_cost_usd": round(row["total_cost"], 4),
            "total_tokens": row["total_tokens"],
            "total_calls": row["calls"],
            "by_agent": [
                {"agent": r["agent_name"], "cost_usd": round(r["cost"], 4), "tokens": r["tokens"], "calls": r["calls"]}
                for r in agent_rows
            ],
        }

    def _period_cutoff(self, period: str) -> str:
        now = datetime.now()
        if period == "today":
            return now.replace(hour=0, minute=0, second=0).isoformat()
        elif period == "week":
            return (now - timedelta(days=7)).isoformat()
        elif period == "month":
            return (now - timedelta(days=30)).isoformat()
        return now.replace(hour=0, minute=0, second=0).isoformat()
