"""
Main server implementation for MCP Search Server.

Provides main entry point for MCP Search server.
All tool logic is encapsulated in the tools module.
"""

import asyncio
import logging

from mcp.server.fastmcp import FastMCP
from .core import settings, setup_logger
from .tools import ToolRegistry

logger = setup_logger(__name__)


def create_app() -> FastMCP:
    """
    Create and configure the MCP Search application.

    Returns:
        FastMCP: Configured MCP server instance.
    """
    mcp = FastMCP("mcp-search")
    tools = ToolRegistry()
    tools.register_tools(mcp)
    return mcp


async def main():
    """
    Main entry point for the MCP Search server.

    Initializes all components and starts the server.
    """
    logger.info("Starting MCP Search Server")
    mcp = create_app()
    await mcp.run_sse_async()


if __name__ == "__main__":
    asyncio.run(main())
