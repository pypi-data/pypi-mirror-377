import json
from datetime import UTC, datetime
from typing import Any, Literal, TypedDict, cast

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
from langgraph.types import Command

from universal_mcp.agents.bigtoolcache.context import Context
from universal_mcp.agents.bigtoolcache.prompts import TOOLS_LIST
from universal_mcp.agents.bigtoolcache.state import State
from universal_mcp.logger import logger
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolFormat


class ToolSelectionOutput(TypedDict):
    connected_tool_ids: list[str]
    unconnected_tool_ids: list[str]


def build_graph(tool_registry: ToolRegistry, llm: BaseChatModel):
    @tool
    async def search_tools(queries: list[str]) -> str:
        """Search tools for a given list of queries
        Each single query should be atomic (doable with a single tool).
        For tasks requiring multiple tools, add separate queries for each subtask"""
        logger.info(f"Searching tools for queries: '{queries}'")
        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": TOOLS_LIST,
                        "cache_control": {"type": "ephemeral", "ttl": "1h"},
                    }
                ],
            },
            {"role": "user", "content": str(queries)},
        ]
        response = llm.with_structured_output(ToolSelectionOutput).invoke(messages)
        response_text = f"Connected tools: {response['connected_tool_ids']}\nUnconnected tools: {response['unconnected_tool_ids']}"
        return response_text

    @tool
    async def load_tools(tool_ids: list[str]) -> list[dict[str, Any]]:
        """Load the tools for the given tool ids. Returns the tool name, description, parameters schema, and output schema. A tool id is made up using the app_id and the tool_name, attached by double underscore (__). e.g. google_mail__send_email"""
        temp_manager = tool_registry.tool_manager
        temp_manager.clear_tools()
        await tool_registry.export_tools(tool_ids, format=ToolFormat.NATIVE)
        tool_details = []
        for tool_id in tool_ids:
            tool = temp_manager.get_tool(tool_id)
            tool_details.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters_schema": tool.parameters,
                    "output_schema": tool.output_schema,
                }
            )
        return tool_details

    @tool
    async def call_tool(tool_id: str, tool_args: dict[str, Any]) -> Any:
        """Call the tool with the given id and arguments."""
        return await tool_registry.call_tool(tool_id, tool_args)

    async def call_model(
        state: State, runtime: Runtime[Context]
    ) -> Command[Literal["select_tools", "call_tools"]]:
        logger.info("Calling model...")
        try:
            system_message = runtime.context.system_prompt.format(
                system_time=datetime.now(tz=UTC).isoformat()
            )
            messages = [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": system_message,
                            "cache_control": {"type": "ephemeral", "ttl": "1h"},
                        }
                    ],
                },
                *state["messages"],
            ]

            model = llm

            if isinstance(model, ChatAnthropic):
                model_with_tools = model.bind_tools(
                    [search_tools, load_tools, call_tool],
                    tool_choice="auto",
                    cache_control={"type": "ephemeral", "ttl": "1h"},
                )
            else:
                model_with_tools = model.bind_tools(
                    [search_tools, load_tools, call_tool], tool_choice="auto"
                )
            response = cast(AIMessage, await model_with_tools.ainvoke(messages))

            if response.tool_calls:
                logger.info(
                    f"Model responded with {len(response.tool_calls)} tool calls."
                )
                if len(response.tool_calls) > 1:
                    raise Exception(
                        "Not possible in Claude with llm.bind_tools(tools=tools, tool_choice='auto')"
                    )
                tool_call = response.tool_calls[0]
                if tool_call["name"] == search_tools.name:
                    logger.info("Model requested to select tools.")
                    return Command(goto="select_tools", update={"messages": [response]})
                elif tool_call["name"] == load_tools.name:
                    logger.info("Model requested to load tools.")
                    tool_details = await load_tools.ainvoke(input=tool_call["args"])
                    tool_msg = ToolMessage(
                        f"Loaded tools. {tool_details}", tool_call_id=tool_call["id"]
                    )
                    selected_tool_ids = tool_call["args"]["tool_ids"]
                    logger.info(f"Loaded tools: {selected_tool_ids}")
                    return Command(
                        goto="call_model",
                        update={
                            "messages": [response, tool_msg],
                            "selected_tool_ids": selected_tool_ids,
                        },
                    )
                elif tool_call["name"] == call_tool.name:
                    logger.info("Model requested to call tool.")
                    return Command(goto="call_tools", update={"messages": [response]})
                return Command(goto="call_tools", update={"messages": [response]})
            else:
                logger.info("Model responded with a message, ending execution.")
                return Command(update={"messages": [response]})
        except Exception as e:
            logger.error(f"Error in call_model: {e}")
            raise

    async def select_tools(
        state: State, runtime: Runtime[Context]
    ) -> Command[Literal["call_model"]]:
        logger.info("Selecting tools...")
        try:
            tool_call = state["messages"][-1].tool_calls[0]
            searched_tools = await search_tools.ainvoke(input=tool_call["args"])
            tool_msg = ToolMessage(
                f"Available tools: {searched_tools}", tool_call_id=tool_call["id"]
            )
            return Command(goto="call_model", update={"messages": [tool_msg]})
        except Exception as e:
            logger.error(f"Error in select_tools: {e}")
            raise

    async def call_tools(state: State) -> Command[Literal["call_model"]]:
        logger.info("Calling tools...")
        outputs = []
        recent_tool_ids = []
        tool_call = state["messages"][-1].tool_calls[0]
        tool_id = tool_call["args"]["tool_id"]
        tool_args = tool_call["args"]["tool_args"]
        logger.info(f"Executing tool: {tool_id} with args: {tool_args}")
        try:
            await tool_registry.export_tools([tool_id], ToolFormat.LANGCHAIN)
            tool_result = await call_tool.ainvoke(
                input={"tool_id": tool_id, "tool_args": tool_args}
            )
            logger.info(f"Tool '{tool_id}' executed successfully.")
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_id,
                    tool_call_id=tool_call["id"],
                ))
            recent_tool_ids.append(tool_call["name"])
        except Exception as e:
            logger.error(f"Error executing tool '{tool_call['name']}': {e}")
            outputs.append(
                ToolMessage(
                    content=json.dumps("Error: " + str(e)),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return Command(
            goto="call_model",
            update={"messages": outputs, "selected_tool_ids": recent_tool_ids},
        )

    builder = StateGraph(State, context_schema=Context)

    builder.add_node(call_model)
    builder.add_node(select_tools)
    builder.add_node(call_tools)
    builder.set_entry_point("call_model")
    return builder
