"""
Example: Code Agent

An agent that can read files, run shell commands, and write code.

Usage:
    python examples/code_agent.py "refactor main.py to use async/await"
"""
import sys
from ai_agents import Agent, Runner
from ai_agents.tools import read_file, write_file, list_files, run_command

agent = Agent(
    name="CodeAgent",
    instructions="""You are an expert software engineer.
You can read and write files, run commands, and help with coding tasks.
Always read relevant files before making changes.
After making changes, run tests if they exist.
Explain what you changed and why.""",
    tools=[read_file, write_file, list_files, run_command],
    model="gpt-4o",
    max_steps=15,
)

if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Help me with my code"
    result = Runner.run(agent, task, verbose=True)
