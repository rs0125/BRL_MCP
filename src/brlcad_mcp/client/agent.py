"""LangGraph ReAct agent that connects to the MCP tool server."""

from __future__ import annotations

import asyncio
import sys

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from brlcad_mcp.config import settings


def _build_model() -> ChatOpenAI:
    """Instantiate the LLM backend."""
    if not settings.llm.api_key:
        print("ERROR: OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)
    return ChatOpenAI(
        model=settings.llm.model,
        temperature=settings.llm.temperature,
    )


async def run_agent() -> None:
    """Launch the interactive CLI agent loop."""
    model = _build_model()

    print("Starting local MCP Client...")
    client = MultiServerMCPClient(
        {
            "brlcad_server": {
                "command": sys.executable,
                "args": ["-m", "brlcad_mcp.server"],
                "transport": "stdio",
            }
        }
    )
    tools = await client.get_tools()
    print(f"Successfully loaded {len(tools)} tool(s) from BRL-CAD!")

    agent = create_react_agent(model, tools)

    print("\n=================================================")
    print(" BRL-CAD Terminal Agent Active. Type 'exit' to quit.")
    print("=================================================")

    while True:
        try:
            user_input = input("\nYou: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if user_input.strip().lower() in {"exit", "quit"}:
            break

        print("AI is calculating geometry...")
        response = await agent.ainvoke(
            {"messages": [("user", user_input)]}
        )
        print(f"\nAI: {response['messages'][-1].content}")


def main() -> None:
    """Synchronous entry point for the agent CLI."""
    asyncio.run(run_agent())
