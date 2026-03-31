"""
Orchestrator — routet Nachrichten zum richtigen Agent.

Liest Agents aus der Registry (nicht hardcoded).
Nutzt OpenAI Function Calling um zu entscheiden welcher Agent passt.
Conversation Memory pro User (max 20 Messages).

Wird von Telegram Bot und Dashboard Chat genutzt.
"""
import json
import logging

import httpx

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = (
    "Du bist der AgentCore24 Assistent.\n"
    "Du hilfst dem User bei seinen Aufgaben.\n"
    "Antworte immer auf Deutsch, kurz und praezise.\n"
    "Wenn du eine Aufgabe an einen Agent delegierst, "
    "erklaere kurz was passiert."
)


class Orchestrator:
    def __init__(self, credential_manager, agent_registry: dict, config: dict = None, cost_tracker=None):
        """
        Args:
            credential_manager: Fuer OpenAI API Key
            agent_registry: {"agent_name": agent_instance, ...}
            config: client.json["orchestrator"] Sektion
            cost_tracker: CostTracker Instanz (optional)
        """
        self.cred_manager = credential_manager
        self.agents = agent_registry
        self.config = config or {}
        self.cost_tracker = cost_tracker
        self.model = self.config.get("model", "gpt-4o-mini")
        self.max_messages = self.config.get("max_conversation_messages", 20)
        self._conversations: dict[str, list] = {}

    def _get_system_prompt(self) -> str:
        return self.config.get("system_prompt", DEFAULT_SYSTEM_PROMPT)

    def _get_messages(self, user_id: str) -> list:
        if user_id not in self._conversations:
            self._conversations[user_id] = [
                {"role": "system", "content": self._get_system_prompt()}
            ]
        return self._conversations[user_id]

    def _build_agent_functions(self) -> list:
        """Baut OpenAI Function Definitions dynamisch aus Agent-Registry."""
        functions = []
        for name, agent in self.agents.items():
            functions.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": agent.description or agent.role,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task": {
                                "type": "string",
                                "description": "Was der Agent tun soll",
                            },
                        },
                        "required": ["task"],
                    },
                },
            })
        return functions

    async def chat(self, message: str, user_id: str = "default") -> str:
        """Hauptmethode — nimmt Nachricht, routet zu Agent, gibt Antwort."""
        try:
            api_key = self.cred_manager.get_api_key("openai")
        except KeyError:
            return "OpenAI API-Key fehlt. Bitte im Dashboard unter Credentials eintragen."

        messages = self._get_messages(user_id)
        messages.append({"role": "user", "content": message})

        # Conversation trimmen
        if len(messages) > self.max_messages + 2:
            messages[:] = [messages[0]] + messages[-(self.max_messages):]

        agent_functions = self._build_agent_functions()

        try:
            result = await self._call_openai(api_key, messages, agent_functions)
            msg = result["choices"][0]["message"]

            # Tool Calls → Agent ausfuehren
            if msg.get("tool_calls"):
                messages.append(msg)
                return await self._handle_agent_calls(msg["tool_calls"], messages, api_key, user_id)

            # Normale Antwort
            answer = msg.get("content", "")
            messages.append({"role": "assistant", "content": answer})
            return answer

        except httpx.HTTPStatusError as e:
            return f"OpenAI Fehler: {e.response.status_code}"
        except Exception as e:
            logger.error(f"Orchestrator Fehler: {e}")
            return f"Fehler: {e}"

    async def _handle_agent_calls(self, tool_calls: list, messages: list, api_key: str, user_id: str) -> str:
        """Fuehrt Agent-Calls aus und generiert Antwort."""
        for tc in tool_calls:
            agent_name = tc["function"]["name"]
            try:
                args = json.loads(tc["function"]["arguments"])
            except json.JSONDecodeError:
                args = {}

            logger.info(f"Orchestrator → Agent '{agent_name}': {args.get('task', '')[:80]}")

            agent = self.agents.get(agent_name)
            if agent:
                result = await agent.execute({"task": args.get("task", ""), "data": args.get("data")})
            else:
                result = {"success": False, "error": f"Agent '{agent_name}' nicht gefunden"}

            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": json.dumps(result, ensure_ascii=False, default=str),
            })

        # Zweiter LLM-Call: Tool-Ergebnisse in Antwort verwandeln
        result = await self._call_openai(api_key, messages)
        answer = result["choices"][0]["message"].get("content", "")
        messages.append({"role": "assistant", "content": answer})
        return answer

    async def _call_openai(self, api_key: str, messages: list, tools: list = None) -> dict:
        """OpenAI API Call mit optionalem Cost Tracking."""
        request_body = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1500,
        }
        if tools:
            request_body["tools"] = tools
            request_body["tool_choice"] = "auto"

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

        # Cost Tracking
        if self.cost_tracker:
            usage = data.get("usage", {})
            await self.cost_tracker.track_llm_call(
                model=self.model,
                input_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
                agent_name="orchestrator",
            )

        return data
