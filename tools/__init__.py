"""
Tools — Wiederverwendbare Funktionen die Agents nutzen.

Tool-Interface (Funktions-basiert):
    TOOL_NAME = "scrape_google_maps"
    TOOL_DESCRIPTION = "Scrapt Leads von Google Maps"
    TOOL_PARAMETERS = { "type": "object", "properties": { ... } }
    async def run(params: dict, context: dict) -> dict

Tool-Interface (Klassen-basiert):
    class MyTool(BaseTool):
        name = "my_tool"
        description = "..."
        parameters_schema = { ... }
        async def run(self, params, context) -> dict

Registry gibt ein Dict zurueck:
    {"tool_name": {"run": callable, "name": str, "description": str, "parameters": dict}}
"""
import importlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_tool_registry(tools_dir: str = None) -> dict:
    """Laedt alle Tools aus dem tools/ Verzeichnis.

    Unterstuetzt beides: Funktions-basiert (run() + Modul-Konstanten)
    und Klassen-basiert (erbt von BaseTool).
    """
    if tools_dir is None:
        tools_dir = str(Path(__file__).parent)

    registry = {}

    for file in sorted(Path(tools_dir).glob("*.py")):
        if file.name.startswith("_") or file.name == "base_tool.py":
            continue

        module_name = file.stem
        try:
            module = importlib.import_module(f"tools.{module_name}")
        except Exception as e:
            logger.warning(f"Tool '{module_name}' konnte nicht geladen werden: {e}")
            continue

        # Klassen-basiert: Suche nach BaseTool-Subklassen
        from tools.base_tool import BaseTool
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseTool)
                and attr is not BaseTool
            ):
                instance = attr()
                registry[instance.name] = {
                    "run": instance.run,
                    "name": instance.name,
                    "description": instance.description,
                    "parameters": instance.parameters_schema,
                }
                break
        else:
            # Funktions-basiert: run() + Modul-Konstanten
            if hasattr(module, "run"):
                name = getattr(module, "TOOL_NAME", module_name)
                registry[name] = {
                    "run": module.run,
                    "name": name,
                    "description": getattr(module, "TOOL_DESCRIPTION", ""),
                    "parameters": getattr(module, "TOOL_PARAMETERS", {}),
                }

    return registry
