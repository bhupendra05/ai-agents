"""Web tools — search and fetch."""
from __future__ import annotations

import urllib.parse
import urllib.request

from ai_agents.tool import tool


@tool
def web_search(query: str, num_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo and return a list of results.

    Args:
        query: The search query string.
        num_results: Number of results to return (default 5).
    """
    encoded = urllib.parse.quote_plus(query)
    url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_redirect=1&no_html=1"
    req = urllib.request.Request(url, headers={"User-Agent": "ai-agents/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            import json
            data = json.loads(resp.read())

        results = []
        # Abstract result
        if data.get("AbstractText"):
            results.append(f"Summary: {data['AbstractText']}\nURL: {data.get('AbstractURL', '')}")

        # Related topics
        for topic in data.get("RelatedTopics", [])[:num_results]:
            if isinstance(topic, dict) and topic.get("Text"):
                results.append(f"- {topic['Text']}\n  {topic.get('FirstURL', '')}")

        if not results:
            return f"No results found for: {query}"

        return "\n\n".join(results[:num_results])

    except Exception as e:
        return f"Search failed: {e}"


@tool
def fetch_url(url: str, max_chars: int = 4000) -> str:
    """
    Fetch the text content of a URL.

    Args:
        url: The URL to fetch.
        max_chars: Maximum number of characters to return (default 4000).
    """
    req = urllib.request.Request(url, headers={"User-Agent": "ai-agents/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read().decode("utf-8", errors="ignore")

        # Strip HTML tags if HTML response
        if "html" in content_type.lower():
            import re
            raw = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL | re.IGNORECASE)
            raw = re.sub(r"<style[^>]*>.*?</style>", "", raw, flags=re.DOTALL | re.IGNORECASE)
            raw = re.sub(r"<[^>]+>", " ", raw)
            raw = re.sub(r"\s+", " ", raw).strip()

        return raw[:max_chars] + ("..." if len(raw) > max_chars else "")

    except Exception as e:
        return f"Failed to fetch {url}: {e}"
