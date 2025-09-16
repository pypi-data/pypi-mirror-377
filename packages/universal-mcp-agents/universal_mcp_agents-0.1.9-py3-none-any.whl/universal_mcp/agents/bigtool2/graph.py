import json
from datetime import UTC, datetime
from typing import Literal, cast
import asyncio

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import BaseTool, tool
from langgraph.graph import StateGraph
from langgraph.types import Command

from universal_mcp.agents.bigtool2.state import State
from universal_mcp.logger import logger
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolFormat


def build_graph(
    tool_registry: ToolRegistry, llm: BaseChatModel, system_prompt: str, default_tools: list[BaseTool]
):
    @tool
    async def search_tools(queries: list[str]) -> str:
        """Search tools for a given list of queries
        Each single query should be atomic (doable with a single tool).
        For tasks requiring multiple tools, add separate queries for each subtask"""
        logger.info(f"Searching tools for queries: '{queries}'")
        try:
            all_tool_candidates = ""
            app_ids = await tool_registry.list_all_apps()
            connections = await tool_registry.list_connected_apps()
            connection_ids = set([connection["app_id"] for connection in connections])
            connected_apps = [
                app["id"] for app in app_ids if app["id"] in connection_ids
            ]
            [
                app["id"] for app in app_ids if app["id"] not in connection_ids
            ]
            app_tools = {}
            for task_query in queries:
                apps_list = await tool_registry.search_apps(task_query, limit=5)
                tools_list = []
                for app in apps_list:
                    tools_list.extend(await tool_registry.search_tools(task_query, limit=5, app_id=app["id"]))
                tool_candidates = [
                    f"{tool['id']}: {tool['description']}" for tool in tools_list
                ]
                for tool in tool_candidates:
                    app = tool.split("__")[0]
                    if app not in app_tools:
                        app_tools[app] = []
                    if len(app_tools[app]) < 5:
                        app_tools[app].append(tool)
            for app in app_tools:
                app_status = "connected" if app in connected_apps else "NOT connected"
                all_tool_candidates += (
                    f"Tools from {app} (status: {app_status} by user):\n"
                )
                for tool in app_tools[app]:
                    all_tool_candidates += f" - {tool}\n"
                all_tool_candidates += "\n"

            return all_tool_candidates
        except Exception as e:
            logger.error(f"Error retrieving tools: {e}")
            return "Error: " + str(e)

    @tool
    async def load_tools(tool_ids: list[str]) -> list[str]:
        """
        Load the tools for the given tool ids. Returns the valid tool ids after loading.
        Tool ids are of form 'appid__toolid'. Example: 'google_mail__send_email'
        """
        correct, incorrect = [], []
        app_tool_list: dict[str, list[str]] = {}

        # Group tool_ids by app for fewer registry calls
        app_to_tools: dict[str, list[str]] = {}
        for tool_id in tool_ids:
            if "__" not in tool_id:
                incorrect.append(tool_id)
                continue
            app, tool = tool_id.split("__", 1)
            app_to_tools.setdefault(app, []).append((tool_id, tool))

        # Fetch all apps concurrently
        async def fetch_tools(app: str):
            try:
                tools_dict = await tool_registry.list_tools(app)
                return app, {tool_unit["name"] for tool_unit in tools_dict}
            except Exception as e:
                return app, None

        results = await asyncio.gather(*(fetch_tools(app) for app in app_to_tools))

        # Build map of available tools per app
        for app, tools in results:
            if tools is not None:
                app_tool_list[app] = tools

        # Validate tool_ids
        for app, tool_entries in app_to_tools.items():
            available = app_tool_list.get(app)
            if available is None:
                incorrect.extend(tool_id for tool_id, _ in tool_entries)
                continue
            for tool_id, tool in tool_entries:
                if tool in available:
                    correct.append(tool_id)
                else:
                    incorrect.append(tool_id)

        return correct

    @tool
    async def web_search(query: str) -> str:
        """Search the web for the given query. Returns the search results. Do not use for app-specific searches (for example, reddit or linkedin searches should be done using the app's tools)"""
        tool = await tool_registry.export_tools(
            ["exa__search_with_filters"], ToolFormat.LANGCHAIN
        )
        response = await tool_registry.call_tool("exa__search_with_filters", {"query": query, "contents": {"summary": True}})
        return response


    async def call_model(
        state: State,
    ) -> Command[Literal["select_tools", "call_tools"]]:
        logger.info("Calling model...")
        try:
            system_message = system_prompt.format(
                system_time=datetime.now(tz=UTC).isoformat()
            )
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
                    selected_tool_ids = await load_tools.ainvoke(tool_call["args"])
                    tool_msg = ToolMessage(
                        f"Loaded tools- {selected_tool_ids}", tool_call_id=tool_call["id"]
                    )
                    logger.info(f"Loaded tools: {selected_tool_ids}")
                    return Command(
                        goto="call_model",
                        update={
                            "messages": [response, tool_msg],
                            "selected_tool_ids": selected_tool_ids,
                        },
                    )

                elif tool_call["name"] == web_search.name:
                    logger.info(f"Tool '{tool_call['name']}' is a web search tool. Proceeding to call.")
                    web_search_result = await web_search.ainvoke(input=tool_call["args"])
                    tool_msg = ToolMessage(
                        f"Web search result: {web_search_result}", tool_call_id=tool_call["id"]
                    )
                    return Command(goto="call_model", update={"messages": [response, tool_msg]})

                elif "ui_tools" in tool_call["name"]:
                    logger.info(f"Tool '{tool_call['name']}' is a UI tool. Proceeding to call.")
                    ui_tool_result = await ui_tools_dict[tool_call["name"]].ainvoke(input=tool_call["args"])
                    tool_msg = ToolMessage(
                        f"UI tool result: {ui_tool_result}", tool_call_id=tool_call["id"]
                    )
                    return Command(goto="call_model", update={"messages": [response, tool_msg]})


                elif tool_call["name"] not in state["selected_tool_ids"]:
                    try:
                        await tool_registry.export_tools(
                            [tool_call["name"]], ToolFormat.LANGCHAIN
                        )
                        logger.info(
                            f"Tool '{tool_call['name']}' not in selected tools, but available. Proceeding to call."
                        )
                        return Command(
                            goto="call_tools", update={"messages": [response]}
                        )
                    except Exception as e:
                        logger.error(
                            f"Unexpected tool call: {tool_call['name']}. Error: {e}"
                        )
                        raise Exception(
                            f"Unexpected tool call: {tool_call['name']}. Available tools: {state['selected_tool_ids']}"
                        ) from e
                logger.info(f"Proceeding to call tool: {tool_call['name']}")
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
                f"Available tool_ids: {searched_tools}. Call load_tools to select the required tools only.", tool_call_id=tool_call["id"]
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
            logger.info(
                f"Executing tool: {tool_call['name']} with args: {tool_call['args']}"
            )
            try:
                await tool_registry.export_tools(
                    [tool_call["name"]], ToolFormat.LANGCHAIN
                )
                tool_result = await tool_registry.call_tool(
                    tool_call["name"], tool_call["args"]
                )
                logger.info(f"Tool '{tool_call['name']}' executed successfully.")
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
