"""Tool definition and decorator."""
from __future__ import annotations

import inspect
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, get_type_hints


@dataclass
class Tool:
    """A callable tool that an agent can use."""

    name: str
    description: str
    func: Callable
    parameters: dict = field(default_factory=dict)

    def __call__(self, **kwargs) -> Any:
        return self.func(**kwargs)

    def to_openai_schema(self) -> dict:
        """Return the tool schema in OpenAI function-calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def to_anthropic_schema(self) -> dict:
        """Return the tool schema in Anthropic Claude tool_use format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Callable:
    """
    Decorator to register a function as an agent tool.

    Usage::

        @tool
        def get_weather(location: str) -> str:
            \"\"\"Get the current weather for a location.\"\"\"
            ...

        @tool(name="search", description="Search the web for information")
        def web_search(query: str, num_results: int = 5) -> list:
            ...
    """
    def decorator(func: Callable) -> Tool:
        tool_name = name or func.__name__
        tool_description = description or (inspect.getdoc(func) or "")

        # Build JSON Schema parameters from type hints + docstring
        params = _build_parameters(func)

        return Tool(
            name=tool_name,
            description=tool_description,
            func=func,
            parameters=params,
        )

    # Support both @tool and @tool() syntax
    if callable(name):
        func = name
        name = None
        return decorator(func)

    return decorator


def _build_parameters(func: Callable) -> dict:
    """Build JSON Schema for function parameters from type hints."""
    sig = inspect.signature(func)
    hints = {}
    try:
        hints = get_type_hints(func)
    except Exception:
        pass

    TYPE_MAP = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }

    properties: dict = {}
    required: list = []

    for param_name, param in sig.parameters.items():
        py_type = hints.get(param_name, str)
        json_type = TYPE_MAP.get(py_type, "string")

        prop: dict = {"type": json_type}

        # Parse description from docstring (Google style)
        doc = inspect.getdoc(func) or ""
        for line in doc.split("\n"):
            stripped = line.strip()
            if stripped.startswith(f"{param_name}:") or stripped.startswith(f"{param_name} ("):
                desc = stripped.split(":", 1)[-1].strip()
                if desc:
                    prop["description"] = desc
                break

        properties[param_name] = prop

        if param.default is inspect.Parameter.empty:
            required.append(param_name)

    schema: dict = {
        "type": "object",
        "properties": properties,
    }
    if required:
        schema["required"] = required

    return schema
