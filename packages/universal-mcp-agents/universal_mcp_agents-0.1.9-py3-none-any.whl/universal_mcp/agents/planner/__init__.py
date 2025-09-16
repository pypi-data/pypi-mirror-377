from langgraph.checkpoint.base import BaseCheckpointSaver
from universal_mcp.tools.registry import ToolRegistry

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.agents.react import ReactAgent

from .graph import build_graph
from .prompts import DEVELOPER_PROMPT


class PlannerAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str,
        registry: ToolRegistry,
        memory: BaseCheckpointSaver | None = None,
        executor_agent_cls: type[BaseAgent] = ReactAgent,
        **kwargs,
    ):
        super().__init__(name, instructions, model, memory, **kwargs)
        self.app_registry = registry
        self.llm = load_chat_model(model)
        self.executor_agent_cls = executor_agent_cls

    def _build_system_message(self):
        return DEVELOPER_PROMPT.format(
            name=self.name, instructions=self.instructions
        )

    async def _build_graph(self):
        return build_graph(
            self.llm,
            self.app_registry,
            self._build_system_message(),
            self.model,
            self.executor_agent_cls,
        ).compile(checkpointer=self.memory)

    @property
    def graph(self):
        return self._graph


__all__ = ["PlannerAgent"]
