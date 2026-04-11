"""
Main server implementation for MCP Search Server.

Provides main entry point for MCP Search server,
including initialization, routing, and startup.
"""

import asyncio
import logging
from typing import Optional

from mcp.server.fastapi import serve
from .server import MCPTools
from .core import (
    settings,
    setup_logger
)


logger = setup_logger(__name__)


class MCPSever:
    """
    Main MCP Search Server class.
    
    Manages lifecycle of the MCP server, including initialization,
    routing, and shutdown procedures.
    """
    
    def __init__(self):
        """Initialize the MCP server."""
        self.tools = MCPTools()
        logger.info("MCP Server initialized")
        
    async def start(self):
        """
        Start the MCP server.
        
        Initializes the server and starts listening for MCP tool calls.
        """
        logger.info(f"Starting MCP Search Server on port {settings.mcp_port}")
        
        try:
            # Configure and start the MCP server
            await serve(
                self.tools.search_web,
                host="0.0.0.0",
                port=settings.mcp_port,
                transport="sse"
            )
        except Exception as e:
            logger.error(f"Failed to start MCP server: {str(e)}")
            raise
            
    async def shutdown(self):
        """Shutdown the MCP server and clean up resources."""
        logger.info("Shutting down MCP Server")
        await self.tools.close()
        logger.info("MCP Server shutdown complete")
        
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.shutdown()


async def main():
    """
    Main entry point for the MCP Search server.
    
    Serves as the primary startup point for the server.
    """
    logger.info("Starting MCP Search Server")
    
    async with MCPSever() as server:
        try:
            await server.start()
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            raise


if __name__ == "__main__":
    # For direct execution
    asyncio.run(main())