"""Agent class — orchestrates tools and LLM calls."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Optional

from .tool import Tool


@dataclass
class Message:
    role: str   # system | user | assistant | tool
    content: Any
    tool_call_id: Optional[str] = None
    tool_name: Optional[str] = None


@dataclass
class AgentResult:
    output: str
    messages: list[Message]
    tool_calls: int


class Agent:
    """
    A ReAct-style LLM agent that loops: Think → Act → Observe → Think...

    Supports OpenAI and Anthropic backends out of the box.
    Custom backends can be used by passing a ``llm_fn`` callable.

    Args:
        name:        Display name for this agent.
        instructions: System prompt — describes the agent's role and behavior.
        tools:       List of Tool objects the agent can call.
        model:       LLM model string (e.g. 'gpt-4o', 'claude-3-5-sonnet-20241022').
        backend:     'openai' | 'anthropic' | 'ollama'. Auto-detected from model name.
        max_steps:   Maximum tool-call iterations before forcing a final answer.
        temperature: LLM temperature (0 = deterministic).
    """

    def __init__(
        self,
        name: str = "Agent",
        instructions: str = "You are a helpful assistant.",
        tools: Optional[list[Tool]] = None,
        model: str = "gpt-4o",
        backend: Optional[str] = None,
        max_steps: int = 10,
        temperature: float = 0.0,
    ):
        self.name = name
        self.instructions = instructions
        self.tools: dict[str, Tool] = {t.name: t for t in (tools or [])}
        self.model = model
        self.backend = backend or _detect_backend(model)
        self.max_steps = max_steps
        self.temperature = temperature

    def run(self, user_message: str, context: Optional[str] = None) -> AgentResult:
        """
        Run the agent on a user message and return the final answer.

        Args:
            user_message: The task or question for the agent.
            context:      Optional extra context prepended to the system prompt.
        """
        system = self.instructions
        if context:
            system = f"{context}\n\n---\n\n{system}"

        messages: list[Message] = [
            Message(role="user", content=user_message),
        ]

        tool_calls_total = 0

        for step in range(self.max_steps):
            response = self._call_llm(system, messages)

            if self.backend == "anthropic":
                output, tool_calls = _parse_anthropic_response(response)
            else:
                output, tool_calls = _parse_openai_response(response)

            # No tool calls → final answer
            if not tool_calls:
                messages.append(Message(role="assistant", content=output))
                return AgentResult(
                    output=output or "",
                    messages=messages,
                    tool_calls=tool_calls_total,
                )

            # Add assistant message with tool calls
            messages.append(Message(role="assistant", content=response))
            tool_calls_total += len(tool_calls)

            # Execute each tool call
            for tc in tool_calls:
                tool_name = tc["name"]
                tool_args = tc["args"]
                call_id = tc.get("id", tool_name)

                if tool_name not in self.tools:
                    result = f"Error: tool '{tool_name}' not found."
                else:
                    try:
                        result = self.tools[tool_name](**tool_args)
                        if not isinstance(result, str):
                            result = json.dumps(result, ensure_ascii=False, default=str)
                    except Exception as e:
                        result = f"Error calling {tool_name}: {e}"

                messages.append(Message(
                    role="tool",
                    content=result,
                    tool_call_id=call_id,
                    tool_name=tool_name,
                ))

        # Max steps exceeded — ask for final answer
        messages.append(Message(
            role="user",
            content="You have reached the maximum number of steps. Provide your final answer now based on what you've found so far.",
        ))
        response = self._call_llm(system, messages)
        if self.backend == "anthropic":
            output, _ = _parse_anthropic_response(response)
        else:
            output, _ = _parse_openai_response(response)

        return AgentResult(
            output=output or "Maximum steps reached.",
            messages=messages,
            tool_calls=tool_calls_total,
        )

    def _call_llm(self, system: str, messages: list[Message]) -> Any:
        if self.backend == "anthropic":
            return _anthropic_call(system, messages, self.model, self.temperature, list(self.tools.values()))
        elif self.backend == "ollama":
            return _openai_call(
                system, messages, self.model, self.temperature, list(self.tools.values()),
                base_url="http://localhost:11434/v1",
                api_key="ollama",
            )
        else:
            return _openai_call(system, messages, self.model, self.temperature, list(self.tools.values()))


# ── Backend helpers ───────────────────────────────────────────────────────────

def _detect_backend(model: str) -> str:
    if model.startswith("claude"):
        return "anthropic"
    if model.startswith("llama") or model.startswith("mistral") or model.startswith("qwen"):
        return "ollama"
    return "openai"


def _openai_call(system, messages, model, temperature, tools, base_url=None, api_key=None):
    from openai import OpenAI
    client = OpenAI(
        api_key=api_key or os.getenv("OPENAI_API_KEY"),
        base_url=base_url,
    )

    formatted = [{"role": "system", "content": system}]
    for m in messages:
        if m.role == "assistant" and not isinstance(m.content, str):
            formatted.append(m.content)  # raw response object
        elif m.role == "tool":
            formatted.append({
                "role": "tool",
                "tool_call_id": m.tool_call_id,
                "content": m.content,
            })
        else:
            formatted.append({"role": m.role, "content": m.content})

    kwargs: dict = {
        "model": model,
        "messages": formatted,
        "temperature": temperature,
    }
    if tools:
        kwargs["tools"] = [t.to_openai_schema() for t in tools]
        kwargs["tool_choice"] = "auto"

    return client.chat.completions.create(**kwargs)


def _anthropic_call(system, messages, model, temperature, tools):
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    formatted = []
    for m in messages:
        if m.role == "assistant":
            if not isinstance(m.content, str):
                # Convert Anthropic response object back
                formatted.append({"role": "assistant", "content": m.content.content})
            else:
                formatted.append({"role": "assistant", "content": m.content})
        elif m.role == "tool":
            # Anthropic tool results go as user messages
            formatted.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": m.tool_call_id,
                    "content": m.content,
                }],
            })
        else:
            formatted.append({"role": m.role, "content": m.content})

    kwargs: dict = {
        "model": model,
        "max_tokens": 4096,
        "system": system,
        "messages": formatted,
    }
    if tools:
        kwargs["tools"] = [t.to_anthropic_schema() for t in tools]

    return client.messages.create(**kwargs)


def _parse_openai_response(response) -> tuple[str, list]:
    msg = response.choices[0].message
    text = msg.content or ""
    tool_calls = []
    if msg.tool_calls:
        for tc in msg.tool_calls:
            tool_calls.append({
                "id": tc.id,
                "name": tc.function.name,
                "args": json.loads(tc.function.arguments),
            })
    return text, tool_calls


def _parse_anthropic_response(response) -> tuple[str, list]:
    text = ""
    tool_calls = []
    for block in response.content:
        if block.type == "text":
            text += block.text
        elif block.type == "tool_use":
            tool_calls.append({
                "id": block.id,
                "name": block.name,
                "args": block.input,
            })
    return text, tool_calls
