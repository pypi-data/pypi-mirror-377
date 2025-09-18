import asyncio
import builtins
import contextlib
import io
from typing import Any

from loguru import logger


async def eval_unsafe(code: str, _locals: dict[str, Any], timeout: int = 10) -> tuple[str, dict[str, Any]]:
    """Executes a string of Python code in a sandboxed environment."""
    # Store original keys before execution
    original_keys = set(_locals.keys())
    result = f"Executing code...\n{code}\n\nOutput:\n"
    result += "=" * 50 + "\n"
    try:
        logger.debug(f"Executing code with timeout {timeout}")
        with contextlib.redirect_stdout(io.StringIO()) as f:
            # Execute the code in the provided locals context
            # This should define an async function `main`
            exec(code, builtins.__dict__, _locals)

            if "main" in _locals and asyncio.iscoroutinefunction(_locals["main"]):
                # Run the main async function
                await asyncio.wait_for(_locals["main"](), timeout=timeout)
            else:
                result += "\nError: No `async def main()` function found in the script."

        output = f.getvalue()
        result += output
        if not output:
            result += "<code ran, no output printed to stdout>"
    except Exception as e:
        result += f"Error during execution: {repr(e)}"

    # Determine new variables created during execution
    new_keys = set(_locals.keys()) - original_keys
    new_vars = {key: _locals[key] for key in new_keys}
    return result, new_vars
