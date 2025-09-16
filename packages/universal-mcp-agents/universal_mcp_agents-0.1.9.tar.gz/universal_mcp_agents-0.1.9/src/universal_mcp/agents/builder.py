import asyncio
from collections.abc import Sequence
from typing import Annotated, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolConfig

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.agents.shared.tool_node import build_tool_node_graph
from universal_mcp.agents.utils import messages_to_list
from collections import defaultdict

class Agent(BaseModel):
    """Agent that can be created by the builder."""

    name: str = Field(description="Name of the agent.")
    description: str = Field(description="A small description of the agent.")
    expertise: str = Field(description="The expertise of the agent.")
    instructions: str = Field(description="The instructions for the agent to follow.")
    schedule: str | None = Field(
        description="The cron expression for the agent to run on.", default=None
    )


class BuilderState(TypedDict):
    user_task: str
    generated_agent: Agent | None
    tool_config: ToolConfig | None
    messages: Annotated[Sequence[BaseMessage], add_messages]


AGENT_BUILDER_INSTRUCTIONS = r"""
You are a specialized Agent Generation AI, tasked with creating intelligent, effective, and context-aware AI agents based on user requests.

When given a user's request, immediately follow this structured process:

# 1. Intent Breakdown
- Clearly identify the primary goal the user wants the agent to achieve.
- Recognize any special requirements, constraints, formatting requests, or interaction rules.
- Summarize your understanding briefly to ensure alignment with user intent.

# 2. Agent Profile Definition
- **Name (2-4 words)**: Concise, clear, and memorable name reflecting core functionality.
- **Description (1-2 sentences)**: Captures the unique value and primary benefit to users.
- **Expertise**: Precise domain-specific expertise area. Avoid vague or overly general titles.
- **Instructions**: Compose detailed, highly actionable system instructions that directly command the agent's behavior. Respond in markdown as this text will be rendered in a rich text editor. Write instructions as clear imperatives, without preamble, assuming the agent identity is already established externally.
- **Schedule**: If the user specifies a schedule, you should also provide a cron expression for the agent to run on. The schedule should be in a proper cron expression and nothing more. Do not respond with any other information or explain your reasoning for the schedule, otherwise this will cause a parsing error that is undesirable.

## ROLE & RESPONSIBILITY
- Clearly state the agent's primary mission, e.g., "Your primary mission is...", "Your core responsibility is...".
- Outline the exact tasks it handles, specifying expected input/output clearly.

## INTERACTION STYLE
- Define exactly how to communicate with users: tone, format, response structure.
- Include explicit commands, e.g., "Always wrap responses in \`\`\`text\`\`\` blocks.", "Never add greetings or meta-information.", "Always provide outputs in user's requested languages."

## OUTPUT FORMATTING RULES
- Clearly specify formatting standards required by the user (e.g., JSON, plain text, markdown).
- Include explicit examples to illustrate correct formatting.

## LIMITATIONS & CONSTRAINTS
- Explicitly define boundaries of the agent's capabilities.
- Clearly state what the agent must never do or say.
- Include exact phrases for declining requests outside scope.

## REAL-WORLD EXAMPLES
Provide two explicit interaction examples showing:
- User's typical request.
- Final agent response demonstrating perfect compliance.

Create an agent that feels thoughtfully designed, intelligent, and professionally reliable, perfectly matched to the user's original intent.
"""


async def generate_agent(
    llm: BaseChatModel, task: str, old_agent: Agent | None = None
) -> Agent:
    """Generates an agent from a task, optionally modifying an existing one."""
    prompt_parts = [AGENT_BUILDER_INSTRUCTIONS]
    if old_agent:
        prompt_parts.append(
            "\nThe user wants to modify the following agent design. "
            "Incorporate their feedback into a new design.\n\n"
            f"{old_agent.model_dump_json(indent=2)}"
        )
    else:
        prompt_parts.append(f"\n\n**Task:** {task}")

    prompt = "\n".join(prompt_parts)
    structured_llm = llm.with_structured_output(Agent)
    agent = await structured_llm.ainvoke(prompt)
    return agent


class BuilderAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str,
        registry: ToolRegistry,
        memory: BaseCheckpointSaver | None = None,
        **kwargs,
    ):
        super().__init__(name, instructions, model, memory, **kwargs)
        self.registry = registry
        self.llm: BaseChatModel = load_chat_model(model)

    async def _create_agent(self, state: BuilderState):
        last_message = state["messages"][-1]
        task = last_message.content
        agent = state.get("generated_agent")

        yield {
            "messages": [
                AIMessage(
                    content="Thinking... I will now design an agent to handle your request.",
                )
            ],
        }
        generated_agent = await generate_agent(self.llm, task, agent)
        yield {
            "user_task": task,
            "generated_agent": generated_agent,
            "messages": [
                AIMessage(
                    content=("I've designed an agent to help you with your task.")
                )
            ],
        }

    async def _create_tool_config(self, state: BuilderState):
        task = state["user_task"]
        yield {
            "messages": [
                AIMessage(
                    content="Great! Now, I will select the appropriate tools for this agent. This may take a moment.",
                )
            ]
        }
        tool_finder_graph = build_tool_node_graph(self.llm, self.registry)
        
        initial_state = {
            "original_task": task,
            "messages": [HumanMessage(content=task)],
            "decomposition_attempts": 0,
        }
        final_state = await tool_finder_graph.ainvoke(initial_state)
        execution_plan = final_state.get("execution_plan")
        tool_config = {}
        if execution_plan:
            # Use defaultdict to easily group tools by app_id
            apps_with_tools = defaultdict(list)
            for step in execution_plan:
                app_id = step.get("app_id")
                tool_ids = step.get("tool_ids")
                if app_id and tool_ids:
                    apps_with_tools[app_id].extend(tool_ids)

            # Convert to a regular dict and remove any duplicate tool_ids for the same app
            tool_config = {
                app_id: list(set(tools)) for app_id, tools in apps_with_tools.items()
            }
            final_message = "I have selected the necessary tools for the agent. The agent is ready!"
        else:
            # Handle the case where the graph failed to create a plan
            final_message = "I was unable to find the right tools for this task. Please try rephrasing your request."

        yield {
            "tool_config": tool_config,
            "messages": [
                AIMessage(content=final_message)
            ],
        }

    async def _build_graph(self):
        builder = StateGraph(BuilderState)
        builder.add_node("create_agent", self._create_agent)
        builder.add_node("create_tool_config", self._create_tool_config)

        builder.add_edge(START, "create_agent")
        builder.add_edge("create_agent", "create_tool_config")
        builder.add_edge("create_tool_config", END)
        return builder.compile(checkpointer=self.memory)


async def main():
    from universal_mcp.agentr.registry import AgentrRegistry

    registry = AgentrRegistry()
    agent = BuilderAgent(
        name="Builder Agent",
        instructions="You are a builder agent that creates other agents.",
        model="gemini/gemini-1.5-pro",
        registry=registry,
    )
    result = await agent.invoke(
        "Send a daily email to manoj@agentr.dev with daily agenda of the day",
    )
    from rich import print
    print(messages_to_list(result["messages"]))
    print(result["generated_agent"])
    print(result["tool_config"])


if __name__ == "__main__":
    asyncio.run(main())
