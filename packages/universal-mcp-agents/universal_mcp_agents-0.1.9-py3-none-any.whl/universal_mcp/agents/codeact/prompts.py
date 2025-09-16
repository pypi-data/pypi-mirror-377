import inspect
import re
from typing import Optional, Sequence

from langchain_core.tools import StructuredTool, tool as create_tool


def make_safe_function_name(name: str) -> str:
    """Convert a tool name to a valid Python function name."""
    # Replace non-alphanumeric characters with underscores
    safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    # Ensure the name doesn't start with a digit
    if safe_name and safe_name[0].isdigit():
        safe_name = f"tool_{safe_name}"
    # Handle empty name edge case
    if not safe_name:
        safe_name = "unnamed_tool"
    return safe_name


def create_default_prompt(
    tools: Sequence[StructuredTool],
    base_prompt: Optional[str] = None,
):
    """Create default prompt for the CodeAct agent."""
    prompt = f"{base_prompt}\n\n" if base_prompt else ""
    prompt += """You will be given a task to perform. You should output either
- a Python code snippet that provides the solution to the task, or a step towards the solution. Any output you want to extract from the code should be printed to the console. Code should be output in a fenced code block.
- text to be shown directly to the user, if you want to ask for more information or provide the final answer.

In addition to the Python Standard Library, you can use the following functions:"""

    for tool in tools:
        # Use coroutine if it exists, otherwise use func
        tool_callable = (
            tool.coroutine
            if hasattr(tool, "coroutine") and tool.coroutine is not None
            else tool.func
        )
        # Create a safe function name
        safe_name = make_safe_function_name(tool.name)
        # Determine if it's an async function
        is_async = inspect.iscoroutinefunction(tool_callable)
        # Add appropriate function definition
        prompt += f'''\n{"async " if is_async else ""}def {safe_name}{str(inspect.signature(tool_callable))}:
    """{tool.description}"""
    ... 
'''

    prompt += """

Variables defined at the top level of previous code snippets can be referenced in your code.

Always use print() statements to explore data structures and function outputs. Simply returning values will not display them back to you for inspection. For example, use print(result) instead of just 'result'.

As you don't know the output schema of the additional Python functions you have access to, start from exploring their contents before building a final solution.

IMPORTANT CODING STRATEGY:
1. Only write code up to the point where you make an API call/tool usage with an output
2. Print the type/shape and a sample entry of this output, and using that knowledge proceed to write the further code

This means:
- Write code that makes the API call or tool usage
- Print the result with type information: print(f"Type: {type(result)}")
- Print the shape/structure: print(f"Shape/Keys: {result.keys() if isinstance(result, dict) else len(result) if isinstance(result, (list, tuple)) else 'N/A'}")
- Print a sample entry: print(f"Sample: {result[0] if isinstance(result, (list, tuple)) and len(result) > 0 else result}")
- Then, based on this knowledge, write the code to process/use this data

Reminder: use Python code snippets to call tools"""
    return prompt


REFLECTION_PROMPT = """
Review the assistant's latest code for as per the quality rules:

<conversation_history>
{conversation_history}
</conversation_history>

If you find ANY of these issues, describe the problem briefly and clearly.
If NO issues are found, respond with EXACTLY: "NONE"
"""

RETRY_PROMPT = """
I need you to completely regenerate your previous response based on this feedback:

'''
{reflection_result}
'''

DO NOT reference the feedback directly. Instead, provide a completely new response that addresses the issues.
"""
