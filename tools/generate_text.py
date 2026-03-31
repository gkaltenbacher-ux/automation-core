"""
Tool: Text generieren via OpenAI.

Referenz-Implementation fuer das Tool-Interface.
"""
import httpx

TOOL_NAME = "generate_text"
TOOL_DESCRIPTION = "Generiert Text mit einem LLM (OpenAI). Fuer E-Mails, Zusammenfassungen, Analysen."
TOOL_PARAMETERS = {
    "type": "object",
    "properties": {
        "prompt": {
            "type": "string",
            "description": "Der Prompt fuer das LLM",
        },
        "system_prompt": {
            "type": "string",
            "description": "System-Prompt (optional)",
        },
        "model": {
            "type": "string",
            "description": "OpenAI Modell (default: gpt-4o-mini)",
        },
        "max_tokens": {
            "type": "integer",
            "description": "Max Tokens (default: 1000)",
        },
    },
    "required": ["prompt"],
}


async def run(params: dict, context: dict) -> dict:
    prompt = params.get("prompt", "")
    system_prompt = params.get("system_prompt", "Du bist ein hilfreicher Assistent. Antworte auf Deutsch.")
    model = params.get("model", "gpt-4o-mini")
    max_tokens = params.get("max_tokens", 1000)

    if not prompt:
        return {"success": False, "error": "Prompt fehlt"}

    get_api_key = context.get("get_api_key")
    if not get_api_key:
        return {"success": False, "error": "get_api_key nicht im Context"}

    try:
        api_key = await get_api_key("openai")
    except KeyError as e:
        return {"success": False, "error": str(e)}

    log = context.get("log")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        if log:
            await log(f"Text generiert ({usage.get('total_tokens', '?')} Tokens)")

        return {
            "success": True,
            "data": {
                "text": text,
                "model": model,
                "tokens": usage,
            },
        }

    except httpx.HTTPStatusError as e:
        return {"success": False, "error": f"OpenAI Fehler: {e.response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
