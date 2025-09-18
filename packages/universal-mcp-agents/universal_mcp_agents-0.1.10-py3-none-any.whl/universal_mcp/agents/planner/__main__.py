import asyncio

from universal_mcp.agentr.registry import AgentrRegistry

from universal_mcp.agents.planner import PlannerAgent
from universal_mcp.agents.utils import messages_to_list


async def main():
    registry = AgentrRegistry()
    agent = PlannerAgent(
        name="planner-agent",
        instructions="You are a helpful assistant.",
        model="azure/gpt-4o",
        registry=registry,
    )
    from rich import print

    print("Starting agent...")
    result = await agent.invoke(
        user_input="Send an email to manoj@agentr.dev with the subject 'testing planner' and body 'This is a test of the planner agent.'",
        thread_id="xyz",
    )
    print(messages_to_list(result["messages"]))


if __name__ == "__main__":
    asyncio.run(main())
