from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.bigtoolcache import BigToolAgentCache


async def agent():
    agent_object = await BigToolAgentCache(
        name="BigTool Agent Cache version",
        instructions="You are a helpful assistant that can use various tools to complete tasks.",
        model="anthropic/claude-4-sonnet-20250514",
        registry=AgentrRegistry(),
    )._build_graph()
    return agent_object
