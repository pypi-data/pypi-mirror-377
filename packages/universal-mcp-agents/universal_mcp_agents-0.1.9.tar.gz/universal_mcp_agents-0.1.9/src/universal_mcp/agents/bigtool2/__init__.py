from langgraph.checkpoint.base import BaseCheckpointSaver

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.logger import logger
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolConfig, ToolFormat

from .graph import build_graph
from .prompts import SYSTEM_PROMPT


class BigToolAgent2(BaseAgent):
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str,
        registry: ToolRegistry,
        memory: BaseCheckpointSaver | None = None,
        tools: ToolConfig | None = None,
        **kwargs,
    ):
        super().__init__(name, instructions, model, memory, **kwargs)

        self.registry = registry
        self.llm = load_chat_model(self.model)
        self.recursion_limit = kwargs.get("recursion_limit", 10)
        self.tools = tools or {}
        if "ui" not in self.tools:
            # self.tools["ui"] = ["create_bar_chart", "create_line_chart", "create_pie_chart", "create_table", "http_get", "http_post", "http_put", "http_delete", "http_patch", "read_file"]
            self.tools["ui"] = ["create_table"]

        logger.info(
            f"BigToolAgent '{self.name}' initialized with model '{self.model}'."
        )

    def _build_system_message(self):
        return SYSTEM_PROMPT.format(
            name=self.name,
            instructions=f"**User Instructions:**\n{self.instructions}",
        )

    async def _build_graph(self):
        """Build the bigtool agent graph using the existing create_agent function."""
        logger.info(f"Building graph for BigToolAgent '{self.name}'...")
        try:
            default_tools = await self.registry.export_tools(self.tools, ToolFormat.LANGCHAIN)
            graph_builder = build_graph(
                tool_registry=self.registry,
                llm=self.llm,
                system_prompt=self._build_system_message(),
                default_tools=default_tools,
            )

            compiled_graph = graph_builder.compile(checkpointer=self.memory)
            logger.info("Graph built and compiled successfully.")
            return compiled_graph
        except Exception as e:
            logger.error(f"Error building graph for BigToolAgent '{self.name}': {e}")
            raise

    @property
    def graph(self):
        return self._graph


__all__ = ["BigToolAgent2"]
