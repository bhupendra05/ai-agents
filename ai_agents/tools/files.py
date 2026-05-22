"""File system tools."""
from __future__ import annotations

import os
from pathlib import Path

from ai_agents.tool import tool


@tool
def read_file(path: str) -> str:
    """
    Read the contents of a file.

    Args:
        path: Path to the file to read.
    """
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"File not found: {path}"
    except Exception as e:
        return f"Error reading {path}: {e}"


@tool
def write_file(path: str, content: str) -> str:
    """
    Write content to a file, creating it if it doesn't exist.

    Args:
        path: Path to write to.
        content: Content to write.
    """
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Written {len(content)} characters to {path}"
    except Exception as e:
        return f"Error writing {path}: {e}"


@tool
def list_files(directory: str, pattern: str = "*") -> str:
    """
    List files in a directory matching an optional glob pattern.

    Args:
        directory: Directory path to list.
        pattern: Glob pattern (default '*' = all files).
    """
    try:
        p = Path(directory)
        if not p.exists():
            return f"Directory not found: {directory}"
        files = sorted(p.glob(pattern))
        if not files:
            return f"No files matching '{pattern}' in {directory}"
        lines = []
        for f in files:
            stat = f.stat()
            size = stat.st_size
            lines.append(f"{'d' if f.is_dir() else '-'}  {size:>10,}  {f.name}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error listing {directory}: {e}"
