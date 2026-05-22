"""Safe math evaluator tool."""
from __future__ import annotations

import math
import operator

from ai_agents.tool import tool

_SAFE_NAMES = {
    k: v for k, v in vars(math).items() if not k.startswith("_")
}
_SAFE_NAMES.update({"abs": abs, "round": round, "min": min, "max": max, "sum": sum})


@tool
def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression safely.

    Args:
        expression: A math expression like '2 ** 10' or 'sqrt(144)' or '(3.14 * 5**2)'.
    """
    try:
        result = eval(expression, {"__builtins__": {}}, _SAFE_NAMES)  # noqa: S307
        return str(result)
    except ZeroDivisionError:
        return "Error: division by zero"
    except Exception as e:
        return f"Error evaluating expression: {e}"
