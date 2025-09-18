import json
from datetime import UTC, datetime
from typing import Literal, cast

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph
from langgraph.types import Command
from universal_mcp.logger import logger
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolFormat

from universal_mcp.agents.bigtool2.meta_tools import create_meta_tools
from universal_mcp.agents.bigtool2.state import State


def build_graph(tool_registry: ToolRegistry, llm: BaseChatModel, system_prompt: str, default_tools: list[BaseTool]):
    # Instantiate meta tools (search, load, web_search)
    search_tools, load_tools, web_search = create_meta_tools(tool_registry)

    async def call_model(
        state: State,
    ) -> Command[Literal["select_tools", "call_tools"]]:
        logger.info("Calling model...")
        try:
            system_message = system_prompt.format(system_time=datetime.now(tz=UTC).isoformat())
            messages = [
                {"role": "system", "content": system_message},
                *state["messages"],
            ]

            logger.info(f"Selected tool IDs: {state['selected_tool_ids']}")
            if len(state["selected_tool_ids"]) > 0:
                selected_tools = await tool_registry.export_tools(
                    tools=state["selected_tool_ids"], format=ToolFormat.LANGCHAIN
                )
                logger.info(f"Exported {len(selected_tools)} tools for model.")
            else:
                selected_tools = []

            model = llm

            tools = [search_tools, load_tools, web_search, *default_tools, *selected_tools]
            # Remove duplicates based on tool name
            seen_names = set()
            unique_tools = []
            for tool in tools:
                if tool.name not in seen_names:
                    seen_names.add(tool.name)
                    unique_tools.append(tool)
            tools = unique_tools
            model_with_tools = model.bind_tools(
                tools,
                tool_choice="auto",
            )
            response = cast(AIMessage, await model_with_tools.ainvoke(messages))

            if response.tool_calls:
                logger.info(f"Model responded with {len(response.tool_calls)} tool calls.")
                return Command(goto="call_tools", update={"messages": [response]})
            else:
                logger.info("Model responded with a message, ending execution.")
                return Command(update={"messages": [response]})
        except Exception as e:
            logger.error(f"Error in call_model: {e}")
            raise

    async def select_tools(state: State) -> Command[Literal["call_model"]]:
        logger.info("Selecting tools...")
        try:
            tool_call = state["messages"][-1].tool_calls[0]
            searched_tools = await search_tools.ainvoke(input=tool_call["args"])
            tool_msg = ToolMessage(
                f"Available tool_ids: {searched_tools}. Call load_tools to select the required tools only.",
                tool_call_id=tool_call["id"],
            )
            return Command(goto="call_model", update={"messages": [tool_msg]})
        except Exception as e:
            logger.error(f"Error in select_tools: {e}")
            raise

    async def call_tools(state: State) -> Command[Literal["call_model"]]:
        logger.info("Calling tools...")
        outputs = []
        recent_tool_ids = []
        for tool_call in state["messages"][-1].tool_calls:
            try:
                # Handle special tools internally (no export needed)
                if tool_call["name"] == search_tools.name:
                    search_result = await search_tools.ainvoke(input=tool_call["args"])
                    outputs.append(
                        ToolMessage(
                            content=search_result,
                            name=tool_call["name"],
                            tool_call_id=tool_call["id"],
                        )
                    )
                    continue

                if tool_call["name"] == load_tools.name:
                    selected_tool_ids = await load_tools.ainvoke(tool_call["args"])
                    outputs.append(
                        ToolMessage(
                            content=json.dumps(f"Loaded tools- {selected_tool_ids}"),
                            name=tool_call["name"],
                            tool_call_id=tool_call["id"],
                        )
                    )
                    recent_tool_ids = selected_tool_ids
                    continue

                if tool_call["name"] == web_search.name:
                    web_search_result = await web_search.ainvoke(input=tool_call["args"])
                    outputs.append(
                        ToolMessage(
                            content=json.dumps(f"Web search result: {web_search_result}"),
                            name=tool_call["name"],
                            tool_call_id=tool_call["id"],
                        )
                    )
                    continue

                # For other tools: export and call via registry
                await tool_registry.export_tools([tool_call["name"]], ToolFormat.LANGCHAIN)
                tool_result = await tool_registry.call_tool(tool_call["name"], tool_call["args"])
                outputs.append(
                    ToolMessage(
                        content=json.dumps(tool_result),
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                    )
                )
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

    builder = StateGraph(State)

    builder.add_node(call_model)
    builder.add_node(select_tools)
    builder.add_node(call_tools)
    builder.set_entry_point("call_model")
    return builder
