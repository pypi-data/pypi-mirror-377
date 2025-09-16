import asyncio

from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.codeact.agent import CodeActAgent
from universal_mcp.agents.utils import messages_to_list


async def main():
    agent = CodeActAgent(
        "CodeAct Agent",
        instructions="Be very concise in your answers.",
        model="azure/gpt-4o",
        tools={"google_mail": ["send_email"]},
        registry=AgentrRegistry(),
    )
    result = await agent.invoke(
        "Send an email to manoj@agentr.dev from my Gmail account with a subject 'testing codeact agent' and body 'This is a test of the codeact agent.'"
    )
    from rich import print

    print(messages_to_list(result["messages"]))


if __name__ == "__main__":
    asyncio.run(main())
