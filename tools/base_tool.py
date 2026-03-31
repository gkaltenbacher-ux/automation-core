"""
BaseTool — Basis-Klasse fuer Tools die mehr Struktur brauchen.

Fuer einfache Tools reicht eine run()-Funktion + Modul-Konstanten.
BaseTool ist fuer Tools die Initialisierung oder komplexere Logik brauchen.
"""


class BaseTool:
    """Basis fuer klassen-basierte Tools."""

    name: str = ""
    description: str = ""
    parameters_schema: dict = {
        "type": "object",
        "properties": {},
    }

    async def run(self, params: dict, context: dict) -> dict:
        """Fuehrt das Tool aus.

        Args:
            params: Tool-spezifische Parameter
            context: get_api_key, log, db, dsgvo

        Returns:
            {"success": True/False, "data": {...}, "error": "..."}
        """
        raise NotImplementedError(f"Tool '{self.name}' hat keine run() Methode")

    def to_openai_function(self) -> dict:
        """Gibt OpenAI Function Calling Definition zurueck."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema,
            },
        }
