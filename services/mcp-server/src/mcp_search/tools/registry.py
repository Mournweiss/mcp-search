"""
Tool registry for MCP Search Server.

Manages registration of MCP tools with the FastMCP application.
"""

import logging
from typing import Optional, List

from mcp.server.fastmcp import FastMCP
from mcp_search.core.exceptions import MCPError, ToolRegistrationError, ToolExecutionError
from .templates import BaseTool, _tool_registry

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registry for managing MCP tools.
    
    Handles registration of all MCP tools with the FastMCP application.
    """

    def __init__(self):
        """Initialize tool registry."""
        logger.info("Tool registry initialized")

    def register_tools(self, mcp: FastMCP) -> None:
        """
        Register all MCP tools with the given FastMCP instance.
        
        Args:
            mcp (FastMCP): The FastMCP application to register tools with.
        """
        logger.info("Registering MCP tools")
        
        for tool_name, tool_instance in _tool_registry.items():
            try:
                if not tool_name:
                    raise ToolRegistrationError(
                        f"Tool '{tool_instance.__class__.__name__}' has no name defined in metadata"
                    )
                
                # Register the tool with MCP
                logger.info(f"Registering tool: {tool_name}")
                
                # Create a wrapper function that calls the tool's execute method
                @mcp.tool()
                async def tool_wrapper(*args, **kwargs):
                    """Wrapper function for tool execution."""
                    try:
                        return await tool_instance.execute(*args, **kwargs)
                    except Exception as e:
                        logger.error(f"Tool execution failed for {tool_name}: {str(e)}")
                        raise ToolExecutionError(
                            f"Failed to execute tool '{tool_name}': {str(e)}",
                            {"tool_name": tool_name, "error": str(e)}
                        )
                
                # Set the function name to match the tool name
                tool_wrapper.__name__ = tool_name
                
            except Exception as e:
                logger.error(f"Failed to register tool {tool_name}: {str(e)}")
                raise
