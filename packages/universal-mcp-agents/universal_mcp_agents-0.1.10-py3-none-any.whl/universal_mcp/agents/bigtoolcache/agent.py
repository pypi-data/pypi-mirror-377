from universal_mcp.agentr.registry import AgentrRegistry

from universal_mcp.agents.bigtoolcache import BigToolAgentCache


async def agent():
    agent_object = await BigToolAgentCache(
        registry=AgentrRegistry(),
    )._build_graph()
    return agent_object
