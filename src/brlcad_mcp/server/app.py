"""FastMCP application instance and server entry point."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from brlcad_mcp.config import settings

# Create the single MCP application instance.
# Tool modules (server/tools/*) import this and register themselves via @mcp.tool().
mcp = FastMCP(settings.server.name)


def serve() -> None:
    """Start the MCP server (used as a CLI entry point)."""
    # Importing tools here ensures they are registered before the server starts,
    # while avoiding circular imports at module level.
    import brlcad_mcp.server.tools  # noqa: F401

    mcp.run()
