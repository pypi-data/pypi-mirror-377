from collections.abc import Callable

from langchain_core.messages import AIMessageChunk
from langchain_core.tools import StructuredTool
from langchain_core.tools import tool as create_tool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph
from universal_mcp.logger import logger
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolConfig, ToolFormat

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.codeact.prompts import (
    REFLECTION_PROMPT,
    RETRY_PROMPT,
    create_default_prompt,
    make_safe_function_name,
)
from universal_mcp.agents.codeact.sandbox import eval_unsafe
from universal_mcp.agents.codeact.state import CodeActState
from universal_mcp.agents.codeact.utils import extract_and_combine_codeblocks
from universal_mcp.agents.llm import load_chat_model


class CodeActAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str,
        memory: BaseCheckpointSaver | None = None,
        tools: ToolConfig | None = None,
        registry: ToolRegistry | None = None,
        sandbox_timeout: int = 20,
        **kwargs,
    ):
        super().__init__(name, instructions, model, memory, **kwargs)
        self.model_instance = load_chat_model(model, thinking=False)
        self.tools_config = tools or {}
        self.registry = registry
        self.eval_fn = eval_unsafe
        self.reflection_prompt = REFLECTION_PROMPT
        self.reflection_model = self.model_instance
        self.max_reflections = 3
        self.tools_context = {}
        self.context = {}
        self.sandbox_timeout = sandbox_timeout
        self.processed_tools: list[StructuredTool | Callable] = []

    async def _build_graph(self):
        if self.tools_config:
            if not self.registry:
                raise ValueError("Tools are configured but no registry is provided")
            # Langchain tools are fine
            exported_tools = await self.registry.export_tools(self.tools_config, ToolFormat.LANGCHAIN)
            self.processed_tools = [t if isinstance(t, StructuredTool) else create_tool(t) for t in exported_tools]

        self.instructions = create_default_prompt(self.processed_tools, self.instructions)

        for tool in self.processed_tools:
            safe_name = make_safe_function_name(tool.name)
            tool_callable = tool.coroutine if hasattr(tool, "coroutine") and tool.coroutine is not None else tool.func
            self.tools_context[safe_name] = tool_callable
        
        self.context = {**self.context, **self.tools_context}

        agent = StateGraph(CodeActState)
        agent.add_node("call_model", self.call_model)
        agent.add_node("sandbox", self.sandbox)

        agent.set_entry_point("call_model")
        agent.add_conditional_edges(
            "call_model",
            self.should_run_sandbox,
            {
                "sandbox": "sandbox",
                END: END,
            },
        )
        agent.add_edge("sandbox", "call_model")
        return agent.compile(checkpointer=self.memory)

    def should_run_sandbox(self, state: CodeActState) -> str:
        last_message = state["messages"][-1]
        if isinstance(last_message.content, str) and "TASK_COMPLETE" in last_message.content:
            return END

        if state.get("script"):
            return "sandbox"
        return END

    def _extract_content(self, response: AIMessageChunk) -> str:
        if isinstance(response.content, list):
            content = " ".join([c.get("text", "") for c in response.content])
        else:
            content = response.content
        return content

    async def call_model(self, state: CodeActState) -> dict:
        model = self.model_instance
        reflection_model = self.reflection_model

        messages = [{"role": "system", "content": self.instructions}] + state["messages"]

        response = await model.ainvoke(messages)

        text_content = self._extract_content(response)
        if not isinstance(text_content, str):
            raise ValueError(f"Content is not a string: {text_content}")
        code = extract_and_combine_codeblocks(text_content)
        logger.debug(f"Code: {code}")

        if self.max_reflections > 0 and code:
            reflection_count = 0
            while reflection_count < self.max_reflections:
                conversation_history = "\n".join(
                    [
                        f'<message role="{("user" if m.type == "human" else "assistant")}">\n{m.content}\n</message>'
                        for m in state["messages"]
                    ]
                )
                conversation_history += f'\n<message role="assistant">\n{response.content}\n</message>'

                formatted_prompt = REFLECTION_PROMPT.format(conversation_history=conversation_history)

                reflection_messages = [
                    {"role": "system", "content": self.reflection_prompt},
                    {"role": "user", "content": formatted_prompt},
                ]
                reflection_result = await reflection_model.ainvoke(reflection_messages)

                if "NONE" in reflection_result.content:
                    break

                retry_prompt = RETRY_PROMPT.format(reflection_result=reflection_result.content)

                regeneration_messages = [
                    {"role": "system", "content": self.instructions},
                    *state["messages"],
                    {"role": "assistant", "content": response.content},
                    {"role": "user", "content": retry_prompt},
                ]
                response = await model.ainvoke(regeneration_messages)

                code = extract_and_combine_codeblocks(response.content)

                if not code:
                    break

                reflection_count += 1

        return {"messages": [response], "script": code}

    async def sandbox(self, state: CodeActState) -> dict:
        output, new_vars = await self.eval_fn(state["script"], self.context, timeout=self.sandbox_timeout)
        self.context = {**self.context, **new_vars}
        return {
            "messages": [AIMessageChunk(content=output.strip())],
            "script": None,
        }
