"""
Agent-Registry — Auto-Discovery aller Agents im agents/ Verzeichnis.

Jeder Agent erbt von BaseAgent. Die Registry instanziiert sie
mit dem passenden Context (Tools, Config, API-Keys).

Nutzung:
    registry = load_agent_registry(tool_registry=tools, config=client_config, context=ctx)
    result = await registry["lead_researcher"].execute({"task": "Finde Leads"})
"""
import importlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_agent_registry(
    agents_dir: str = None,
    tool_registry: dict = None,
    config: dict = None,
    context: dict = None,
) -> dict:
    """Laedt alle Agents aus dem agents/ Verzeichnis.

    Args:
        agents_dir: Pfad zum agents/ Verzeichnis
        tool_registry: Dict von Tools (aus load_tool_registry)
        config: client.json (Abschnitt "agents" mit Agent-spezifischer Config)
        context: Basis-Context (get_api_key, log, db, etc.)

    Returns:
        {"agent_name": agent_instance, ...}
    """
    if agents_dir is None:
        agents_dir = str(Path(__file__).parent)

    if tool_registry is None:
        tool_registry = {}
    if config is None:
        config = {}
    if context is None:
        context = {}

    agents_config = config.get("agents", {})
    registry = {}

    from agents.base_agent import BaseAgent

    for file in sorted(Path(agents_dir).glob("*.py")):
        if file.name.startswith("_") or file.name == "base_agent.py":
            continue

        module_name = file.stem
        try:
            module = importlib.import_module(f"agents.{module_name}")
        except Exception as e:
            logger.warning(f"Agent '{module_name}' konnte nicht geladen werden: {e}")
            continue

        # Suche nach BaseAgent-Subklassen
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseAgent)
                and attr is not BaseAgent
            ):
                agent_name = attr.name if hasattr(attr, "name") and attr.name != "base" else module_name

                # Agent-spezifische Config aus client.json
                agent_config = agents_config.get(agent_name, {})

                # Nur Tools zuweisen die der Agent braucht UND die existieren
                agent_tools = {}
                tool_names = agent_config.get("tools", getattr(attr, "tools", []))
                for tn in tool_names:
                    if tn in tool_registry:
                        agent_tools[tn] = tool_registry[tn]

                # Context fuer diesen Agent zusammenbauen
                agent_context = {
                    **context,
                    "tool_registry": agent_tools,
                    "config": agent_config,
                }

                try:
                    instance = attr(agent_context)
                    # Tool-Liste aus Config uebernehmen falls vorhanden
                    if "tools" in agent_config:
                        instance.tools = agent_config["tools"]

                    # Deaktivierte Agents nicht registrieren
                    if agent_config.get("enabled", True) is False:
                        logger.info(f"Agent '{agent_name}' ist deaktiviert")
                        continue

                    registry[agent_name] = instance
                    logger.info(f"Agent '{agent_name}' geladen ({len(agent_tools)} Tools)")
                except Exception as e:
                    logger.warning(f"Agent '{agent_name}' Fehler bei Initialisierung: {e}")

                break  # Nur eine Agent-Klasse pro Datei

    return registry
