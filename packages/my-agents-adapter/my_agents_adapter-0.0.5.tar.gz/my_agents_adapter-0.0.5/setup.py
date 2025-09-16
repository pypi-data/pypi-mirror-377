import re
from pathlib import Path
from typing import Any, Match, cast

from setuptools import find_packages, setup

CURRENT_DIR = Path(__file__).resolve().parent

with open((CURRENT_DIR / "src" / "agents_adapter" / "_version.py"), "r") as fd:
    match = re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE)
    if match:
        version = cast(Match[Any], match).group(1)
    else:
        raise RuntimeError("Cannot find version information")

setup(
    name="my-agents-adapter",
    version=version,
    description="test version for agents adapter",
    author="Microsoft Corporation",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[
        "azure-monitor-opentelemetry",
        "azure-ai-projects",
        "azure-identity",
        "starlette",
        "uvicorn",
    ],
    extras_require={
        "agentframework": ["agent-framework"],
        "langgraph": [
            "langchain",
            "langchain-openai",  # to support azure openai clients
            "langgraph",
        ],
    },
)
