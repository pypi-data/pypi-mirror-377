import asyncio

from universal_mcp.agentr.client import AgentrClient
from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.types import ToolFormat


async def main():
    client = AgentrClient()
    registry = AgentrRegistry(client=client)
    await registry.export_tools(["scraper__linkedin_retrieve_profile"], ToolFormat.LANGCHAIN)
    await registry.call_tool("scraper__linkedin_retrieve_profile", {"identifier": "manojbajaj95"})


if __name__ == "__main__":
    asyncio.run(main())
