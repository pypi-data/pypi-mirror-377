import asyncio
from typing import Any

from langchain_core.tools import BaseTool, tool
from universal_mcp.logger import logger
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolFormat


def create_meta_tools(tool_registry: ToolRegistry) -> list[BaseTool]:
    @tool
    async def search_tools(queries: list[str]) -> str:
        """Search tools for a given list of queries
        Each single query should be atomic (doable with a single tool).
        For tasks requiring multiple tools, add separate queries for each subtask"""
        logger.info(f"Searching tools for queries: '{queries}'")
        try:
            all_tool_candidates = ""

            async def fetch_app_and_connection_metadata():
                return await asyncio.gather(
                    tool_registry.list_all_apps(),
                    tool_registry.list_connected_apps(),
                )

            app_ids, connections = await fetch_app_and_connection_metadata()
            connection_ids = set([connection["app_id"] for connection in connections])
            connected_apps = [app["id"] for app in app_ids if app["id"] in connection_ids]
            app_tools: dict[str, list[str]] = {}

            async def find_tools_for_app(task_query: str, app_id: str) -> list[dict[str, Any]]:
                return await tool_registry.search_tools(task_query, limit=5, app_id=app_id)

            async def find_tools_for_query(task_query: str) -> list[str]:
                apps_list = await tool_registry.search_apps(task_query, limit=5)
                per_app_tool_lists = await asyncio.gather(
                    *(find_tools_for_app(task_query, app_entry["id"]) for app_entry in apps_list)
                )
                tools_flat = [tool for sublist in per_app_tool_lists for tool in sublist]
                return [f"{tool['id']}: {tool['description']}" for tool in tools_flat]

            # Run all queries concurrently
            query_results = await asyncio.gather(*(find_tools_for_query(q) for q in queries))

            # Aggregate per-app with cap of 5 per app across all queries
            for tool_desc in [tool for result in query_results for tool in result]:
                app = tool_desc.split("__")[0]
                if app not in app_tools:
                    app_tools[app] = []
                if len(app_tools[app]) < 5 and tool_desc not in app_tools[app]:
                    app_tools[app].append(tool_desc)
            for app in app_tools:
                app_status = "connected" if app in connected_apps else "NOT connected"
                all_tool_candidates += f"Tools from {app} (status: {app_status} by user):\n"
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
            except Exception:
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
        await tool_registry.export_tools(["exa__search_with_filters"], ToolFormat.LANGCHAIN)
        response = await tool_registry.call_tool(
            "exa__search_with_filters", {"query": query, "contents": {"summary": True}}
        )
        return response

    return [search_tools, load_tools, web_search]
