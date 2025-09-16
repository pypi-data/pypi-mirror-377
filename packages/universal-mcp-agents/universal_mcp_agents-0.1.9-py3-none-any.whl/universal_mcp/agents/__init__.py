from universal_mcp.agents.autoagent import AutoAgent
from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.bigtool import BigToolAgent
from universal_mcp.agents.bigtool2 import BigToolAgent2
from universal_mcp.agents.builder import BuilderAgent
from universal_mcp.agents.planner import PlannerAgent
from universal_mcp.agents.react import ReactAgent
from universal_mcp.agents.simple import SimpleAgent
from universal_mcp.agents.codeact import CodeActAgent


def get_agent(agent_name: str):
    if agent_name == "auto":
        return AutoAgent
    elif agent_name == "react":
        return ReactAgent
    elif agent_name == "simple":
        return SimpleAgent
    elif agent_name == "builder":
        return BuilderAgent
    elif agent_name == "planner":
        return PlannerAgent
    elif agent_name == "bigtool":
        return BigToolAgent
    elif agent_name == "bigtool2":
        return BigToolAgent2
    elif agent_name == "codeact":
        return CodeActAgent
    else:
        raise ValueError(f"Unknown agent: {agent_name}. Possible values: auto, react, simple, builder, planner, bigtool, bigtool2, codeact")

__all__ = [
    "BaseAgent",
    "ReactAgent",
    "SimpleAgent",
    "AutoAgent",
    "BigToolAgent",
    "PlannerAgent",
    "BuilderAgent",
    "BigToolAgent2",
]
