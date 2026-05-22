"""
Example: Research Agent

An agent that can search the web, fetch URLs, and write reports to files.

Usage:
    python examples/research_agent.py
"""
import os
from ai_agents import Agent, Runner
from ai_agents.tools import web_search, fetch_url, write_file

agent = Agent(
    name="ResearchAgent",
    instructions="""You are a research assistant. When given a topic:
1. Search for recent information about it
2. Fetch the most relevant URLs for more detail
3. Write a concise, well-structured summary
4. Save the summary to a file if asked

Always cite your sources.""",
    tools=[web_search, fetch_url, write_file],
    model="gpt-4o",
)

if __name__ == "__main__":
    Runner.chat(agent)
