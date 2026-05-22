"""
Example: Custom Tool

Shows how to define your own tools with the @tool decorator.

Usage:
    python examples/custom_tool.py
"""
import random
from ai_agents import Agent, Runner, tool


@tool
def roll_dice(sides: int = 6, count: int = 1) -> str:
    """
    Roll one or more dice and return the results.

    Args:
        sides: Number of sides on each die (default 6).
        count: Number of dice to roll (default 1).
    """
    rolls = [random.randint(1, sides) for _ in range(count)]
    total = sum(rolls)
    return f"Rolled {count}d{sides}: {rolls} (total: {total})"


@tool
def get_quote(category: str = "inspiration") -> str:
    """
    Get a motivational quote.

    Args:
        category: Quote category — inspiration, wisdom, or humor.
    """
    quotes = {
        "inspiration": "The only way to do great work is to love what you do. — Steve Jobs",
        "wisdom": "In the middle of difficulty lies opportunity. — Albert Einstein",
        "humor": "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
    }
    return quotes.get(category, quotes["inspiration"])


agent = Agent(
    name="GameMaster",
    instructions="You are a fun game master. Use dice and quotes to make interactions engaging.",
    tools=[roll_dice, get_quote],
    model="gpt-4o",
)

if __name__ == "__main__":
    Runner.chat(agent)
