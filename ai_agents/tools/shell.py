"""Shell command tool."""
from __future__ import annotations

import subprocess

from ai_agents.tool import tool


@tool
def run_command(command: str, timeout: int = 30) -> str:
    """
    Run a shell command and return its output.

    Args:
        command: The shell command to execute.
        timeout: Timeout in seconds (default 30).
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\n(exit code: {result.returncode})"
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout}s"
    except Exception as e:
        return f"Error running command: {e}"
