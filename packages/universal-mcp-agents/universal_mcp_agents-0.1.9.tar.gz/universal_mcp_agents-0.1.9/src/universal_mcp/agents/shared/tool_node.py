import asyncio
from typing import Annotated, TypedDict, List, Dict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from loguru import logger
from pydantic import BaseModel, Field
from universal_mcp.tools.registry import ToolRegistry

from universal_mcp.agents.shared.prompts import (
    APP_SEARCH_QUERY_PROMPT,
    REVISE_DECOMPOSITION_PROMPT,
    TASK_DECOMPOSITION_PROMPT,
    TOOL_SEARCH_QUERY_PROMPT,
    TOOL_SELECTION_PROMPT,
)


MAX_DECOMPOSITION_ATTEMPTS = 2

# --- Pydantic Models for Structured LLM Outputs ---

class TaskDecomposition(BaseModel):
    sub_tasks: List[str] = Field(description="A list of sub-task descriptions.")

class SearchQuery(BaseModel):
    query: str = Field(description="A concise search query.")

class ToolSelection(BaseModel):
    tool_ids: List[str] = Field(description="The IDs of the selected tools.")


# --- LangGraph Agent State ---

class SubTask(TypedDict, total=False):
    """Represents a single step in the execution plan."""
    task: str
    status: str  # "pending", "success", "failed"
    app_id: str
    tool_ids: List[str]
    reasoning: str

class AgentState(TypedDict):
    """The central state of our agent graph."""
    original_task: str
    decomposition_attempts: int
    failed_sub_task_info: str  # To inform re-decomposition
    sub_tasks: List[SubTask]
    execution_plan: List[SubTask]
    messages: Annotated[list[AnyMessage], add_messages]


# --- Graph Builder ---

def build_tool_node_graph(llm: BaseChatModel, registry: ToolRegistry) -> StateGraph:
    """Builds the adaptive LangGraph workflow for tool selection."""

    async def _decompose_task(state: AgentState) -> AgentState:
        """Decomposes the main task or revises a failed decomposition."""
        attempts = state.get("decomposition_attempts", 0)
        task = state["original_task"]
        failed_info = state.get("failed_sub_task_info")

        if attempts > 0 and failed_info:
            logger.warning(f"Revising decomposition. Attempt {attempts + 1}.")
            prompt = REVISE_DECOMPOSITION_PROMPT.format(
                task=task, failed_sub_task=failed_info
            )
        else:
            logger.info("Performing initial task decomposition.")
            prompt = TASK_DECOMPOSITION_PROMPT.format(task=task)

        response = await llm.with_structured_output(TaskDecomposition).ainvoke(prompt)
        sub_tasks = [
            {"task": sub_task_str, "status": "pending"}
            for sub_task_str in response.sub_tasks
        ]
        
        return {
            "sub_tasks": sub_tasks,
            "decomposition_attempts": attempts + 1,
            "messages": [AIMessage(content=f"New plan created with {len(sub_tasks)} steps.")],
        }

    async def _resolve_sub_tasks(state: AgentState) -> AgentState:
        """Iterates through sub-tasks, providing full plan context to the app selection prompt."""
        sub_tasks = state["sub_tasks"]
        original_task = state["original_task"]
        current_plan = []

        for i, sub_task in enumerate(sub_tasks):
            task_desc = sub_task["task"]
            logger.info(f"Resolving sub-task: '{task_desc}'")

            # 1. Build the FULL context string from the entire plan so far
            if not current_plan:
                plan_context_str = "None. This is the first step."
            else:
                context_lines = [
                    f"- The sub-task '{step['task']}' was assigned to app '{step['app_id']}'."
                    for step in current_plan
                ]
                plan_context_str = "\n".join(context_lines)

            # 2. Generate the App-specific query using the NEW full-context prompt
            app_query_prompt = APP_SEARCH_QUERY_PROMPT.format(
                original_task=original_task,
                plan_context=plan_context_str,
                sub_task=task_desc
            )
            app_query_response = await llm.with_structured_output(SearchQuery).ainvoke(app_query_prompt)
            app_search_query = app_query_response.query
            logger.info(f"Generated context-aware app search query: '{app_search_query}'")

            # 3. Search for candidate apps (the rest of the logic is the same)
            candidate_apps = await registry.search_apps(query=app_search_query, limit=5)
            if not candidate_apps:
                logger.error(f"No apps found for query '{app_search_query}' from sub-task: '{task_desc}'")
                return {"failed_sub_task_info": task_desc, "sub_tasks": []}

            # 4. Generate Action-specific query for finding the tool
            tool_query_prompt = TOOL_SEARCH_QUERY_PROMPT.format(sub_task=task_desc)
            tool_query_response = await llm.with_structured_output(SearchQuery).ainvoke(tool_query_prompt)
            tool_search_query = tool_query_response.query
            logger.info(f"Generated tool search query: '{tool_search_query}'")

            # 5. Find a suitable tool within the candidate apps
            tool_found = False
            for app in candidate_apps:
                app_id = app["id"]
                logger.info(f"Searching for tools in app '{app_id}' with query '{tool_search_query}'...")

                found_tools = await registry.search_tools(query=tool_search_query, app_id=app_id, limit=5)
                if not found_tools:
                    continue

                tool_candidates_str = "\n - ".join([f"{tool['name']}: {tool['description']}" for tool in found_tools])
                selection_prompt = TOOL_SELECTION_PROMPT.format(sub_task=task_desc, tool_candidates=tool_candidates_str)
                selection_response = await llm.with_structured_output(ToolSelection).ainvoke(selection_prompt)

                if selection_response.tool_ids:
                    logger.success(f"Found and selected tool(s) {selection_response.tool_ids} in app '{app_id}'.")
                    sub_task.update({
                        "status": "success",
                        "app_id": app_id,
                        "tool_ids": selection_response.tool_ids,
                        "reasoning": f"Selected tool(s) {selection_response.tool_ids} from app '{app_id}' for sub-task."
                    })
                    current_plan.append(sub_task)
                    tool_found = True
                    break

            if not tool_found:
                logger.error(f"Could not find any suitable tool for sub-task: '{task_desc}'")
                return {"failed_sub_task_info": task_desc, "sub_tasks": []}

        return {"execution_plan": current_plan, "sub_tasks": []}
    
    def _handle_planning_failure(state: AgentState) -> AgentState:
        """Handles the case where all decomposition attempts have failed."""
        logger.error("Maximum decomposition attempts reached. Planning failed.")
        return {
            "messages": [AIMessage(content="I am unable to create a complete plan for this task with the available tools. Please try rephrasing your request.")]
        }

    def _consolidate_plan(state: AgentState) -> AgentState:
        """
        NEW: Merges steps in the execution plan that use the same app_id.
        It combines their tool_ids into a single unique list.
        """
        logger.info("Consolidating final execution plan.")
        plan = state["execution_plan"]
        merged_apps: Dict[str, SubTask] = {}

        for step in plan:
            app_id = step["app_id"]
            if app_id not in merged_apps:
                # Store the first occurrence of this app
                merged_apps[app_id] = step.copy()
                merged_apps[app_id]["tool_ids"] = set(step["tool_ids"])
            else:
                # If app already seen, just update its set of tool_ids
                merged_apps[app_id]["tool_ids"].update(step["tool_ids"])

        # Convert the merged dictionary back to a list of SubTasks
        final_plan = []
        for app_id, step_data in merged_apps.items():
            step_data["tool_ids"] = sorted(list(step_data["tool_ids"]))
            final_plan.append(step_data)
        
        return {"execution_plan": final_plan}


    # --- Graph Definition ---

    workflow = StateGraph(AgentState)

    workflow.add_node("decompose_task", _decompose_task)
    workflow.add_node("resolve_sub_tasks", _resolve_sub_tasks)
    workflow.add_node("consolidate_plan", _consolidate_plan) # NEW NODE
    workflow.add_node("handle_planning_failure", _handle_planning_failure)

    workflow.set_entry_point("decompose_task")

    def should_continue(state: AgentState):
        if not state.get("sub_tasks"): # Resolution failed or succeeded
            if state.get("execution_plan"):
                return "consolidate_plan" # MODIFIED: Go to consolidate on success
            elif state["decomposition_attempts"] >= MAX_DECOMPOSITION_ATTEMPTS:
                return "handle_planning_failure"
            else:
                return "decompose_task" # Re-try decomposition
        else:
            return "resolve_sub_tasks"

    workflow.add_conditional_edges("decompose_task", lambda s: "resolve_sub_tasks")
    workflow.add_conditional_edges("resolve_sub_tasks", should_continue)
    
    workflow.add_edge("consolidate_plan", END) # NEW EDGE
    workflow.add_edge("handle_planning_failure", END)

    return workflow.compile()


async def main():
    """Main function to run the agent."""
    from universal_mcp.agentr.registry import AgentrRegistry
    from universal_mcp.agents.llm import load_chat_model

    registry = AgentrRegistry()
    llm = load_chat_model("anthropic/claude-4-sonnet-20250514")
    
    graph = build_tool_node_graph(llm, registry)

    task = "Find my latest order confirmation in Gmail, search for reviews of the main product on perplexity, and then send an email to ankit@agentr.dev telling about the reviews"
    
    initial_state = {
        "original_task": task,
        "messages": [HumanMessage(content=task)],
        "decomposition_attempts": 0,
    }

    final_state = await graph.ainvoke(initial_state)

    print("\n--- Final Agent State ---")
    if final_state.get("execution_plan"):
        print("Successfully created a consolidated execution plan:")
        for step in final_state["execution_plan"]:
            print(f"- Sub-task: {step['task']}")
            print(f"  - App: {step['app_id']}")
            print(f"  - Tool(s): {', '.join(step['tool_ids'])}")
    else:
        print("Failed to create an execution plan.")
        print(f"Final message: {final_state['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())