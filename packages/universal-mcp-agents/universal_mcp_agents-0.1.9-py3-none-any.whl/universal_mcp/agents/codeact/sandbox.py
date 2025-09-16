import asyncio
import builtins
import contextlib
import io
from typing import Any


async def eval_unsafe(code: str, _locals: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """
    Execute code in a non-blocking way and return the output and changed variables.
    """
    result = f"Executing code...\n{code}\n\nOutput:\n"
    result += "=" * 50 + "\n"

    # Create a combined globals/locals environment that includes builtins
    # and the provided context. This allows nested functions to access tools.
    execution_env = {**builtins.__dict__, **_locals}

    def sync_eval_in_thread():
        """Synchronously execute code and capture output."""
        try:
            with contextlib.redirect_stdout(io.StringIO()) as f:
                exec(code, execution_env)
            output = f.getvalue()
            if not output:
                output = "<code ran, no output printed to stdout>"
            return output
        except Exception as e:
            return f"Error during execution: {repr(e)}"

    # Run the synchronous exec in a separate thread to avoid blocking the event loop.
    output = await asyncio.to_thread(sync_eval_in_thread)
    result += output

    # Identify all variables that are not part of the original builtins
    # and were not in the initial _locals, or were changed.
    changed_vars = {}
    builtin_keys = set(builtins.__dict__.keys())

    for key, value in execution_env.items():
        if key in builtin_keys:
            continue  # Skip builtins

        # Check if the key is new or if the value has changed
        if key not in _locals or _locals[key] is not value:
            changed_vars[key] = value

    return result, changed_vars
