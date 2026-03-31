"""
BaseAgent — Basis-Klasse fuer alle Sub-Agents.

Jeder Sub-Agent erbt von BaseAgent und definiert:
  - name: Eindeutiger Name
  - role: Was der Agent macht (fuer System-Prompt)
  - description: Beschreibung fuer den Orchestrator
  - tools: Liste von Tool-Namen (aus tools/)
  - execute(): Hauptlogik
"""
import json
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class BaseAgent:
    """Basis fuer alle Sub-Agents im System."""

    name: str = "base"
    role: str = "Basis-Agent"
    description: str = ""
    tools: list[str] = []
    model: str = "gpt-4o-mini"
    max_tokens: int = 1000

    def __init__(self, context: dict):
        """
        context enthaelt:
          - get_api_key: async fn(service) -> key
          - log: async fn(message, level)
          - db: Datenbank-Zugriff (optional)
          - config: Agent-spezifische Config aus client.json
          - tool_registry: Dict von verfuegbaren Tools
          - dsgvo: DSGVOManager (optional)
          - cost_tracker: CostTracker (optional)
        """
        self.context = context
        self.log = context.get("log", self._noop_log)
        self.get_api_key = context.get("get_api_key")
        self.config = context.get("config", {})
        self._tool_registry = context.get("tool_registry", {})

        # Config kann model/max_tokens ueberschreiben
        if "model" in self.config:
            self.model = self.config["model"]
        if "max_tokens" in self.config:
            self.max_tokens = self.config["max_tokens"]
        if "system_prompt" in self.config:
            self._custom_system_prompt = self.config["system_prompt"]
        else:
            self._custom_system_prompt = None

    async def execute(self, input_data: dict) -> dict:
        """Hauptmethode — wird vom Orchestrator aufgerufen.

        Args:
            input_data: {"task": "...", "data": {...}}

        Returns:
            {"success": True/False, "data": {...}, "error": "..."}
        """
        raise NotImplementedError(f"Agent '{self.name}' hat keine execute() Methode")

    async def use_tool(self, tool_name: str, params: dict) -> dict:
        """Ruft ein Tool aus der Registry auf."""
        tool = self._tool_registry.get(tool_name)
        if not tool:
            return {"success": False, "error": f"Tool '{tool_name}' nicht gefunden"}
        return await tool["run"](params, self.context)

    async def call_llm(self, messages: list, tools_for_llm: list = None) -> dict:
        """Ruft OpenAI mit Function Calling auf.

        Returns:
            {"content": str, "tool_calls": list | None, "usage": dict}
        """
        try:
            api_key = await self.get_api_key("openai")
        except KeyError as e:
            return {"content": None, "error": str(e)}

        request_body = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": 0.7,
        }
        if tools_for_llm:
            request_body["tools"] = tools_for_llm
            request_body["tool_choice"] = "auto"

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=request_body,
                )
                resp.raise_for_status()
                data = resp.json()

            msg = data["choices"][0]["message"]
            usage = data.get("usage", {})

            # Cost tracking wenn verfuegbar
            cost_tracker = self.context.get("cost_tracker")
            if cost_tracker:
                await cost_tracker.track_llm_call(
                    model=self.model,
                    input_tokens=usage.get("prompt_tokens", 0),
                    output_tokens=usage.get("completion_tokens", 0),
                    agent_name=self.name,
                )

            return {
                "content": msg.get("content"),
                "tool_calls": msg.get("tool_calls"),
                "usage": usage,
            }

        except httpx.HTTPStatusError as e:
            return {"content": None, "error": f"OpenAI Fehler: {e.response.status_code}"}
        except Exception as e:
            return {"content": None, "error": str(e)}

    async def execute_with_tools(self, task: str, data: dict = None) -> dict:
        """Standard-Ablauf: LLM entscheidet welche Tools es braucht, fuehrt sie aus.

        Dies ist die typische execute()-Implementation die Sub-Agents nutzen koennen.
        """
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": self._build_task_message(task, data)},
        ]

        tools_for_llm = self.get_available_tools_for_llm()

        # Erste LLM-Runde
        result = await self.call_llm(messages, tools_for_llm)

        if result.get("error"):
            return {"success": False, "error": result["error"]}

        # Tool Calls verarbeiten (max 5 Runden)
        rounds = 0
        while result.get("tool_calls") and rounds < 5:
            rounds += 1
            messages.append({"role": "assistant", "content": result.get("content"), "tool_calls": result["tool_calls"]})

            for tc in result["tool_calls"]:
                fn_name = tc["function"]["name"]
                try:
                    args = json.loads(tc["function"]["arguments"])
                except json.JSONDecodeError:
                    args = {}

                await self.log(f"Agent {self.name}: Tool {fn_name} aufgerufen")
                tool_result = await self.use_tool(fn_name, args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(tool_result, ensure_ascii=False, default=str),
                })

            result = await self.call_llm(messages, tools_for_llm)
            if result.get("error"):
                return {"success": False, "error": result["error"]}

        return {
            "success": True,
            "data": {
                "response": result.get("content", ""),
                "rounds": rounds,
            },
        }

    def get_system_prompt(self) -> str:
        """System-Prompt — custom aus Config oder generiert."""
        if self._custom_system_prompt:
            return self._custom_system_prompt

        tools_desc = ", ".join(self.tools) if self.tools else "keine"
        return (
            f"Du bist der {self.name} Agent.\n"
            f"Rolle: {self.role}\n"
            f"Verfuegbare Tools: {tools_desc}\n"
            f"Antworte immer auf Deutsch, kurz und praezise."
        )

    def get_available_tools_for_llm(self) -> list:
        """Gibt OpenAI Function Definitions fuer alle Tools dieses Agents zurueck."""
        definitions = []
        for tool_name in self.tools:
            tool = self._tool_registry.get(tool_name)
            if not tool:
                continue
            definitions.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool.get("parameters", {"type": "object", "properties": {}}),
                },
            })
        return definitions

    def _build_task_message(self, task: str, data: dict = None) -> str:
        if data:
            return f"Aufgabe: {task}\n\nDaten:\n{json.dumps(data, ensure_ascii=False, indent=2, default=str)}"
        return f"Aufgabe: {task}"

    @staticmethod
    async def _noop_log(msg, level="info"):
        pass
