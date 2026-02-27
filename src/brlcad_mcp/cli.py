"""CLI entry point for brlcad-mcp.

Usage
-----
    brlcad-mcp serve    # start the MCP tool server
    brlcad-mcp chat     # start the interactive agent
"""

from __future__ import annotations

import argparse
import sys


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="brlcad-mcp",
        description="BRL-CAD Model Context Protocol agent and server.",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("serve", help="Start the MCP tool server (stdio transport)")
    sub.add_parser("chat", help="Start the interactive agent CLI")

    return parser


def main(argv: list[str] | None = None) -> None:
    """Parse CLI arguments and dispatch to the appropriate sub-command."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "serve":
        from brlcad_mcp.server.app import serve

        serve()
    elif args.command == "chat":
        from brlcad_mcp.client.agent import main as agent_main

        agent_main()
    else:
        parser.print_help()
        sys.exit(1)
