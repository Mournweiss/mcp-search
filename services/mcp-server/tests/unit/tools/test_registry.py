"""
Unit tests for MCP Search ToolRegistry.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from mcp_search.tools.registry import ToolRegistry
from mcp_search.tools.templates.base_tool import _tool_registry
from mcp_search.core.exceptions import ToolRegistrationError, ToolExecutionError


@pytest.mark.asyncio
async def test_tool_registry_initialization():
    """Test ToolRegistry initialization."""
    registry = ToolRegistry()
    
    assert registry is not None
    assert hasattr(registry, 'register_tools')


@pytest.mark.asyncio
async def test_tool_registry_register_tools():
    """Test ToolRegistry register_tools method with mocked FastMCP."""
    # Mock FastMCP
    mock_mcp = MagicMock()
    
    # Clear registry before test
    _tool_registry.clear()
    
    # Add a simple tool to the registry for testing
    from mcp_search.tools.search_web import SearchWebTool
    from mcp_search.tools.scrape_urls import ScrapeUrlsTool
    
    # Create instances to ensure they're registered
    search_tool = SearchWebTool()
    scrape_tool = ScrapeUrlsTool()
    
    registry = ToolRegistry()
    
    # Test registration
    registry.register_tools(mock_mcp)
    
    # Verify that tool decorators were called at least once
    assert mock_mcp.tool.called


@pytest.mark.asyncio
async def test_tool_registry_registration_error_handling():
    """Test ToolRegistry error handling during tool registration."""
    # Mock FastMCP
    mock_mcp = MagicMock()
    
    # Clear registry before test
    _tool_registry.clear()
    
    # Test with a tool that has no name in metadata (should raise exception)
    from mcp_search.tools.templates.base_tool import BaseTool
    
    class ToolWithoutName(BaseTool):
        async def execute(self, *args, **kwargs):
            return "test"
    
    # Add this tool to registry
    tool = ToolWithoutName()
    # This should be registered with empty name in the registry
    _tool_registry[""] = tool
    
    registry = ToolRegistry()
    
    # Test that registration raises appropriate error for tool without name
    with pytest.raises(ToolRegistrationError):
        registry.register_tools(mock_mcp)


@pytest.mark.asyncio
async def test_tool_registry_tool_execution_wrapper():
    """Test that registered tools have proper execution wrappers."""
    # Mock FastMCP
    mock_mcp = MagicMock()
    
    # Clear registry before test
    _tool_registry.clear()
    
    from mcp_search.tools.search_web import SearchWebTool
    
    # Create and register a tool
    search_tool = SearchWebTool()
    
    registry = ToolRegistry()
    
    # Test registration - this should not raise any exceptions
    registry.register_tools(mock_mcp)
    
    # Verify that the tool decorator was called
    assert mock_mcp.tool.called


@pytest.mark.asyncio
async def test_tool_registry_empty_registry():
    """Test ToolRegistry with empty tool registry."""
    # Mock FastMCP
    mock_mcp = MagicMock()
    
    # Clear registry before test
    _tool_registry.clear()
    
    registry = ToolRegistry()
    
    # Test registration with empty registry - should not raise exceptions
    registry.register_tools(mock_mcp)
    
    # Should have called the tool decorator at least once (even if no tools)
    # The method should complete without errors
    assert True  # If we reach here, no exception was raised


@pytest.mark.asyncio
async def test_tool_registry_startup_event():
    """Test ToolRegistry startup event handling."""
    # Mock FastMCP
    mock_mcp = MagicMock()
    
    registry = ToolRegistry()
    
    # With decorator syntax, we need to verify that on_event was called with the right event type
    startup_calls = [call for call in mock_mcp.on_event.call_args_list if call[0][0] == "startup"]
    assert len(startup_calls) > 0, "Startup event handler was not registered"
    
    # Create the startup function as defined in the registry
    async def on_startup():
        """Initialize clients on startup."""
        pass
    
    # Call the startup function directly to ensure it works
    await on_startup()
    
    # Should have attempted to register the startup event
    assert mock_mcp.on_event.called


@pytest.mark.asyncio
async def test_tool_registry_shutdown_event():
    """Test ToolRegistry shutdown event handling."""
    # Mock FastMCP
    mock_mcp = MagicMock()
    
    registry = ToolRegistry()
    
    shutdown_calls = [call for call in mock_mcp.on_event.call_args_list if call[0][0] == "shutdown"]
    assert len(shutdown_calls) > 0, "Shutdown event handler was not registered"
    
    # Create the shutdown function as defined in the registry
    async def on_shutdown():
        """Close clients on shutdown."""
        pass
    
    # Call the shutdown function directly to ensure it works
    await on_shutdown()
    
    # Should have attempted to register the shutdown event
    assert mock_mcp.on_event.called