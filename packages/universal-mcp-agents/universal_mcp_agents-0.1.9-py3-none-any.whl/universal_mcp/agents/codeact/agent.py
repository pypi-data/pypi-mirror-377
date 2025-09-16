import inspect
from typing import Callable, Union

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import StructuredTool, tool as create_tool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph
from loguru import logger
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolConfig, ToolFormat

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.agents.codeact.prompts import (
    create_default_prompt,
    make_safe_function_name,
    REFLECTION_PROMPT,
    RETRY_PROMPT,
)
from universal_mcp.agents.codeact.sandbox import eval_unsafe
from universal_mcp.agents.codeact.state import CodeActState
from universal_mcp.agents.codeact.utils import extract_and_combine_codeblocks


class CodeActAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str,
        memory: BaseCheckpointSaver | None = None,
        tools: ToolConfig | None = None,
        registry: ToolRegistry | None = None,
        *,
        reflection_prompt: str = None,
        reflection_model: BaseChatModel = None,
        max_reflections: int = 3,
        **kwargs,
    ):
        super().__init__(name, instructions, model, memory, **kwargs)
        self.model_instance = load_chat_model(model)
        self.tools_config = tools or {}
        self.registry = registry
        self.eval_fn = eval_unsafe
        self.reflection_prompt = reflection_prompt
        self.reflection_model = reflection_model or self.model_instance
        self.max_reflections = max_reflections if reflection_prompt else 0
        self.tools_context = {}
        self.processed_tools: list[Union[StructuredTool, Callable]] = []

    async def _build_graph(self):
        if self.tools_config:
            if not self.registry:
                raise ValueError("Tools are configured but no registry is provided")
            # Langchain tools are fine
            exported_tools = await self.registry.export_tools(
                self.tools_config, ToolFormat.LANGCHAIN
            )
            self.processed_tools = [
                t if isinstance(t, StructuredTool) else create_tool(t)
                for t in exported_tools
            ]

        self.instructions = create_default_prompt(
            self.processed_tools, self.instructions
        )

        for tool in self.processed_tools:
            safe_name = make_safe_function_name(tool.name)
            tool_callable = (
                tool.coroutine
                if hasattr(tool, "coroutine") and tool.coroutine is not None
                else tool.func
            )
            self.tools_context[safe_name] = tool_callable

        agent = StateGraph(CodeActState)
        agent.add_node("call_model", lambda state, config: self.call_model(state, config))
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
        if state.get("script"):
            return "sandbox"
        return END

    def call_model(self, state: CodeActState, config: dict) -> dict:
        context = config.get("context", {})
        instructions = context.get("system_prompt", self.instructions)
        model = self.model_instance
        reflection_model = self.reflection_model

        messages = [{"role": "system", "content": instructions}] + state["messages"]

        response = model.invoke(messages)

        code = extract_and_combine_codeblocks(response.content)

        if self.max_reflections > 0 and code:
            reflection_count = 0
            while reflection_count < self.max_reflections:
                conversation_history = "\n".join(
                    [
                        f'<message role="{("user" if m.type == "human" else "assistant")}">\n{m.content}\n</message>'
                        for m in state["messages"]
                    ]
                )
                conversation_history += (
                    f'\n<message role="assistant">\n{response.content}\n</message>'
                )

                formatted_prompt = REFLECTION_PROMPT.format(
                    conversation_history=conversation_history
                )

                reflection_messages = [
                    {"role": "system", "content": self.reflection_prompt},
                    {"role": "user", "content": formatted_prompt},
                ]
                reflection_result = reflection_model.invoke(reflection_messages)

                if "NONE" in reflection_result.content:
                    break

                retry_prompt = RETRY_PROMPT.format(
                    reflection_result=reflection_result.content
                )

                regeneration_messages = [
                    {"role": "system", "content": instructions},
                    *state["messages"],
                    {"role": "assistant", "content": response.content},
                    {"role": "user", "content": retry_prompt},
                ]
                response = model.invoke(regeneration_messages)

                code = extract_and_combine_codeblocks(response.content)

                if not code:
                    break

                reflection_count += 1

        if code:
            return {"messages": [response], "script": code}
        else:
            return {"messages": [response], "script": None}

    async def sandbox(self, state: CodeActState) -> dict:
        existing_context = state.get("context", {})
        context = {**existing_context, **self.tools_context}
        if inspect.iscoroutinefunction(self.eval_fn):
            output, new_vars = await self.eval_fn(state["script"], context)
        else:
            output, new_vars = self.eval_fn(state["script"], context)
        new_context = {**existing_context, **new_vars}
        return {
            "messages": [{"role": "user", "content": output}],
            "context": new_context,
        }