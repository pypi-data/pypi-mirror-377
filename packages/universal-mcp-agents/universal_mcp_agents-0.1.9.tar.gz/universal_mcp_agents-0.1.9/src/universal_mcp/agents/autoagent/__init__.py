from langgraph.checkpoint.base import BaseCheckpointSaver
from universal_mcp.tools.registry import ToolRegistry

from universal_mcp.agents.autoagent.graph import build_graph
from universal_mcp.agents.base import BaseAgent


class AutoAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str,
        memory: BaseCheckpointSaver | None = None,
        registry: ToolRegistry | None = None,
        **kwargs,
    ):
        super().__init__(name, instructions, model, memory, **kwargs)
        self.tool_registry = registry

    async def _build_graph(self):
        builder = await build_graph(self.tool_registry, self.instructions)
        return builder.compile(checkpointer=self.memory)

    @property
    def graph(self):
        return self._graph


__all__ = ["AutoAgent"]
