import asyncio

from loguru import logger

from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.bigtool2 import BigToolAgent2
from universal_mcp.agents.utils import messages_to_list


async def main():
    agent = BigToolAgent2(
        name="bigtool",
        instructions="You are a helpful assistant that can use tools to help the user.",
        model="azure/gpt-4.1",
        registry=AgentrRegistry(),
    )
    await agent.ainit()
    output = await agent.invoke(
        user_input="Send an email to manoj@agentr.dev"
    )
    logger.info(messages_to_list(output["messages"]))


if __name__ == "__main__":
    asyncio.run(main())
