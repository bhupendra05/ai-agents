# ai-agents

> Minimal Python framework for building LLM-powered agents. Define tools with a decorator, hand them to an agent, and it loops: Think → Act → Observe → Answer.

![Python](https://img.shields.io/badge/python-3.10+-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![OpenAI](https://img.shields.io/badge/backend-OpenAI%20%7C%20Anthropic%20%7C%20Ollama-orange)

```python
from ai_agents import Agent, Runner, tool

@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    return f"Sunny, 22°C in {location}"  # Replace with real API call

agent = Agent(
    name="WeatherBot",
    instructions="You are a helpful weather assistant.",
    tools=[get_weather],
    model="gpt-4o",
)

result = Runner.run(agent, "What's the weather in Tokyo and Paris?", verbose=True)
print(result.output)
```

```
Agent: WeatherBot
Task: What's the weather in Tokyo and Paris?

────────────────────────────────────────────────
Tool calls: 2
╭─ WeatherBot ──────────────────────────────────╮
│ The weather is sunny and 22°C in both Tokyo   │
│ and Paris right now.                          │
╰───────────────────────────────────────────────╯
```

## Why ai-agents?

Most agent frameworks are bloated. This one is ~500 lines total:
- `tool.py` — `@tool` decorator builds JSON Schema from type hints automatically
- `agent.py` — ReAct loop, works with OpenAI, Anthropic, and Ollama
- `runner.py` — pretty output and interactive chat REPL
- Built-in tools — web search, file I/O, shell, calculator

## Installation

```bash
pip install ai-agents
```

Or from source:

```bash
git clone https://github.com/bhupendra05/ai-agents.git
cd ai-agents
pip install -e .
```

Set your API key:

```bash
export OPENAI_API_KEY="sk-..."      # for OpenAI models
export ANTHROPIC_API_KEY="sk-..."   # for Claude models
# Ollama needs no key — just run: ollama serve
```

---

## Quick Start

### 1. Define a tool with `@tool`

```python
from ai_agents import tool

@tool
def search_docs(query: str, max_results: int = 5) -> str:
    """Search the documentation for a query."""
    # Your implementation here
    return f"Found results for: {query}"
```

The decorator reads your function signature + docstring to build the JSON Schema automatically. No YAML, no config files.

### 2. Create an Agent

```python
from ai_agents import Agent

agent = Agent(
    name="DocsBot",
    instructions="You are a technical documentation assistant.",
    tools=[search_docs],
    model="gpt-4o",          # or "claude-3-5-sonnet-20241022" or "llama3.2"
    max_steps=10,            # max tool-call iterations
    temperature=0.0,
)
```

### 3. Run it

```python
from ai_agents import Runner

# One-shot run
result = Runner.run(agent, "How do I configure authentication?", verbose=True)
print(result.output)
print(f"Tool calls made: {result.tool_calls}")

# Interactive chat
Runner.chat(agent)
```

---

## Built-in Tools

```python
from ai_agents.tools import (
    web_search,   # DuckDuckGo search
    fetch_url,    # Fetch and parse webpage content
    read_file,    # Read file contents
    write_file,   # Write to a file
    list_files,   # List directory contents
    run_command,  # Execute shell commands
    calculate,    # Safe math evaluator
)
```

Use them directly or as inspiration for your own tools.

---

## Backends

| Backend | Models | API Key |
|---------|--------|---------|
| **OpenAI** (default) | `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo` | `OPENAI_API_KEY` |
| **Anthropic** | `claude-3-5-sonnet-20241022`, `claude-3-opus` | `ANTHROPIC_API_KEY` |
| **Ollama** | `llama3.2`, `mistral`, `qwen2.5-coder` | None (local) |

Backend is auto-detected from the model name. Or specify explicitly:

```python
agent = Agent(model="llama3.2", backend="ollama")
```

---

## Examples

### Research Agent

```python
from ai_agents import Agent, Runner
from ai_agents.tools import web_search, fetch_url, write_file

agent = Agent(
    name="Researcher",
    instructions="Search the web, read pages, and write a detailed report.",
    tools=[web_search, fetch_url, write_file],
    model="gpt-4o",
)
Runner.chat(agent)
```

### Code Agent

```python
from ai_agents import Agent, Runner
from ai_agents.tools import read_file, write_file, run_command

agent = Agent(
    name="Coder",
    instructions="You are a senior engineer. Read code, make changes, run tests.",
    tools=[read_file, write_file, run_command],
    model="claude-3-5-sonnet-20241022",
    max_steps=20,
)
result = Runner.run(agent, "Add input validation to app/api/users.py", verbose=True)
```

See the `examples/` directory for runnable examples.

---

## Project Structure

```
ai-agents/
├── ai_agents/
│   ├── __init__.py     # Public API: Agent, tool, Tool, Runner
│   ├── agent.py        # ReAct loop + OpenAI/Anthropic/Ollama backends
│   ├── tool.py         # @tool decorator + JSON Schema builder
│   ├── runner.py       # CLI runner + interactive chat
│   └── tools/          # Built-in tools
│       ├── web.py      # web_search, fetch_url
│       ├── files.py    # read_file, write_file, list_files
│       ├── shell.py    # run_command
│       └── calculator.py
├── examples/
│   ├── research_agent.py
│   ├── code_agent.py
│   └── custom_tool.py
└── setup.py
```

## License

MIT © bhupendra05
