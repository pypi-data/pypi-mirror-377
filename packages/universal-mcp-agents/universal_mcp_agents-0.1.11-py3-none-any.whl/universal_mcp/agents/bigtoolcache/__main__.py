import asyncio

from loguru import logger
from universal_mcp.agentr.registry import AgentrRegistry

from universal_mcp.agents.bigtoolcache import BigToolAgentCache


async def main():
    agent = BigToolAgentCache(
        registry=AgentrRegistry(),
    )
    async for event in agent.stream(
        user_input="Send an email to manoj@agentr.dev",
        thread_id="test123",
    ):
        logger.info(event.content)


if __name__ == "__main__":
    asyncio.run(main())
