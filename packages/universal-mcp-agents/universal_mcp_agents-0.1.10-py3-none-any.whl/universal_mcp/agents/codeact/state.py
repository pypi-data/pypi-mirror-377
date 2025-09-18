from typing import Any

from langgraph.graph import MessagesState


class CodeActState(MessagesState):
    """State for CodeAct agent."""

    script: str | None
    """The Python code script to be executed."""
