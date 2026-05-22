"""Runner — CLI and streaming runner for agents."""
from __future__ import annotations

from typing import Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule

from .agent import Agent, AgentResult

console = Console()


class Runner:
    """
    Interactive or programmatic runner for Agent objects.

    Provides pretty-printing, streaming output, and a chat REPL.
    """

    @staticmethod
    def run(agent: Agent, task: str, verbose: bool = False) -> AgentResult:
        """Run an agent on a task and return the result."""
        if verbose:
            console.print(f"\n[bold cyan]Agent:[/bold cyan] {agent.name}")
            console.print(f"[dim]Task:[/dim] {task}\n")
            console.print(Rule(style="dim"))

        result = agent.run(task)

        if verbose:
            console.print(Rule(style="dim"))
            if result.tool_calls:
                console.print(f"[dim]Tool calls:[/dim] {result.tool_calls}")
            console.print(Panel(
                Markdown(result.output),
                title=f"[bold green]{agent.name}[/bold green]",
                border_style="green",
            ))

        return result

    @staticmethod
    def chat(agent: Agent):
        """Start an interactive chat session with an agent."""
        console.print(Panel(
            f"[bold]{agent.name}[/bold]\n[dim]{agent.instructions[:120]}[/dim]",
            title="Agent Chat",
            border_style="cyan",
        ))
        console.print("[dim]Type 'exit' or 'quit' to end the session.[/dim]\n")

        while True:
            try:
                user_input = console.input("[bold blue]You:[/bold blue] ").strip()
            except (KeyboardInterrupt, EOFError):
                console.print("\n[dim]Exiting...[/dim]")
                break

            if user_input.lower() in {"exit", "quit", "q"}:
                console.print("[dim]Goodbye![/dim]")
                break

            if not user_input:
                continue

            with console.status("[dim]Thinking...[/dim]"):
                result = agent.run(user_input)

            console.print(f"\n[bold green]{agent.name}:[/bold green]")
            console.print(Markdown(result.output))
            if result.tool_calls:
                console.print(f"[dim](used {result.tool_calls} tool call(s))[/dim]")
            console.print()
