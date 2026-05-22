from setuptools import setup, find_packages

setup(
    name="ai-agents",
    version="0.1.0",
    description="Minimal Python framework for building LLM-powered ReAct agents",
    author="bhupendra05",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "openai>=1.0",
        "anthropic>=0.30",
        "rich>=13.0",
    ],
    extras_require={
        "dev": ["pytest", "ruff"],
    },
)
