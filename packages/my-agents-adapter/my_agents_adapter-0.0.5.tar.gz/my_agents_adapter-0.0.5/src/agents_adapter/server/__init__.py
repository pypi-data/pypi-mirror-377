__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from .base import FoundryCBAgent


def from_agent_framework(agent):
    from .agent_framework import AgentFrameworkCBAgent

    return AgentFrameworkCBAgent(agent)


def from_langgraph(agent):
    from .langgraph import LangGraphAdapter

    return LangGraphAdapter(agent)


__all__ = ["FoundryCBAgent", "from_agent_framework", "from_langgraph"]
