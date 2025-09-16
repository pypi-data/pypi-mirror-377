import json
from typing import Literal, TypedDict, cast

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph
from langgraph.types import Command
from universal_mcp.logger import logger
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolFormat

from universal_mcp.agents.bigtool.state import State

from .prompts import SELECT_TOOL_PROMPT


def build_graph(
    tool_registry: ToolRegistry,
    llm: BaseChatModel,
    system_prompt: str,
):
    @tool
    async def retrieve_tools(task_query: str) -> list[str]:
        """Retrieve tools for a given task.
        Task query should be atomic (doable with a single tool).
        For tasks requiring multiple tools, call this tool multiple times for each subtask."""
        logger.info(f"Retrieving tools for task: '{task_query}'")
        try:
            tools_list = await tool_registry.search_tools(task_query, limit=10)
            tool_candidates = [
                f"{tool['id']}: {tool['description']}" for tool in tools_list
            ]
            logger.info(f"Found {len(tool_candidates)} candidate tools.")

            class ToolSelectionOutput(TypedDict):
                tool_names: list[str]

            model = llm
            app_ids = await tool_registry.list_all_apps()
            connections = await tool_registry.list_connected_apps()
            connection_ids = set([connection["app_id"] for connection in connections])
            connected_apps = [
                app["id"] for app in app_ids if app["id"] in connection_ids
            ]
            unconnected_apps = [
                app["id"] for app in app_ids if app["id"] not in connection_ids
            ]
            app_id_descriptions = (
                "These are the apps connected to the user's account:\n"
                + "\n".join([f"{app}" for app in connected_apps])
            )
            if unconnected_apps:
                app_id_descriptions += "\n\nOther (not connected) apps: " + "\n".join(
                    [f"{app}" for app in unconnected_apps]
                )

            response = await model.with_structured_output(
                schema=ToolSelectionOutput, method="json_mode"
            ).ainvoke(
                SELECT_TOOL_PROMPT.format(
                    app_ids=app_id_descriptions,
                    tool_candidates="\n - ".join(tool_candidates),
                    task=task_query,
                )
            )

            selected_tool_names = cast(ToolSelectionOutput, response)["tool_names"]
            logger.info(f"Selected tools: {selected_tool_names}")
            return selected_tool_names
        except Exception as e:
            logger.error(f"Error retrieving tools: {e}")
            return []


    async def call_model(
        state: State
    ) -> Command[Literal["select_tools", "call_tools"]]:
        logger.info("Calling model...")
        try:
            messages = [
                {"role": "system", "content": system_prompt},
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

            model_with_tools = llm.bind_tools(
                [retrieve_tools, *selected_tools], tool_choice="auto"
            )


            response = await model_with_tools.ainvoke(messages)
            cast(AIMessage, response)
            logger.debug(f"Response: {response}")


            if response.tool_calls:
                logger.info(
                    f"Model responded with {len(response.tool_calls)} tool calls."
                )
                if len(response.tool_calls) > 1:
                    raise Exception(
                        "Not possible in Claude with llm.bind_tools(tools=tools, tool_choice='auto')"
                    )
                tool_call = response.tool_calls[0]
                if tool_call["name"] == retrieve_tools.name:
                    logger.info("Model requested to select tools.")
                    return Command(goto="select_tools", update={"messages": [response]})
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

    async def select_tools(
        state: State
    ) -> Command[Literal["call_model"]]:
        logger.info("Selecting tools...")
        try:
            tool_call = state["messages"][-1].tool_calls[0]
            selected_tool_names = await retrieve_tools.ainvoke(input=tool_call["args"])
            tool_msg = ToolMessage(
                f"Available tools: {selected_tool_names}", tool_call_id=tool_call["id"]
            )
            logger.info(f"Tools selected: {selected_tool_names}")
            return Command(
                goto="call_model",
                update={
                    "messages": [tool_msg],
                    "selected_tool_ids": selected_tool_names,
                },
            )
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
