"""
Templates package for MCP Search Server tools.

Contains base classes and templates for tool implementations.
"""

from .base_tool import BaseTool, _tool_registry

__all__ = [
    "BaseTool",
    "_tool_registry"
]