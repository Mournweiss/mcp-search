"""
Unit tests for MCP Search BaseTool.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from mcp_search.tools.templates.base_tool import BaseTool, _tool_registry
from mcp_search.clients import SearxNGClient, FirecrawlClient, RedisClient
from mcp_search.core.exceptions import MCPError


@pytest.mark.asyncio
async def test_base_tool_initialization():
    """Test BaseTool initialization."""
    # Clear registry before test
    _tool_registry.clear()
    
    class TestTool(BaseTool):
        async def execute(self, *args, **kwargs):
            return "test"
    
    tool = TestTool()
    
    assert tool is not None
    assert hasattr(tool, 'searxng_client')
    assert hasattr(tool, 'firecrawl_client')
    assert hasattr(tool, 'redis_client')
    assert isinstance(tool.searxng_client, SearxNGClient)
    assert isinstance(tool.firecrawl_client, FirecrawlClient)
    assert isinstance(tool.redis_client, RedisClient)


@pytest.mark.asyncio
async def test_base_tool_abstract_method():
    """Test that BaseTool cannot be instantiated directly."""
    # This should raise TypeError because execute is abstract
    with pytest.raises(TypeError):
        tool = BaseTool()


@pytest.mark.asyncio
async def test_base_tool_registration():
    """Test that BaseTool registers itself in the global registry."""
    # Clear registry before test
    _tool_registry.clear()
    
    # Create a tool with metadata
    class TestToolWithMetadata(BaseTool):
        tool_metadata = {
            "name": "test_tool",
            "description": "A test tool"
        }
        
        async def execute(self, *args, **kwargs):
            return "test"
    
    # Create instance, should register itself
    tool = TestToolWithMetadata()
    
    # Check that it was registered
    assert "test_tool" in _tool_registry
    assert _tool_registry["test_tool"] is tool


@pytest.mark.asyncio
async def test_base_tool_context_manager():
    """Test BaseTool context manager functionality."""
    # Clear registry before test
    _tool_registry.clear()
    
    class TestTool(BaseTool):
        async def execute(self, *args, **kwargs):
            return "test"
    
    tool = TestTool()
    
    # Test context manager usage
    async with tool as t:
        assert t is tool
    
    # Should have been properly entered and exited


@pytest.mark.asyncio
async def test_base_tool_close_method():
    """Test BaseTool close method."""
    # Clear registry before test
    _tool_registry.clear()
    
    class TestTool(BaseTool):
        async def execute(self, *args, **kwargs):
            return "test"
    
    tool = TestTool()
    
    # Mock the close methods of clients
    with patch.object(tool.searxng_client, 'close', new_callable=AsyncMock) as mock_searxng_close, \
         patch.object(tool.firecrawl_client, 'close', new_callable=AsyncMock) as mock_firecrawl_close, \
         patch.object(tool.redis_client, 'close', new_callable=AsyncMock) as mock_redis_close:
        
        # Call close method
        await tool.close()
        
        # Verify all client close methods were called
        mock_searxng_close.assert_called_once()
        mock_firecrawl_close.assert_called_once()
        mock_redis_close.assert_called_once()


@pytest.mark.asyncio
async def test_base_tool_client_instantiation():
    """Test that BaseTool properly instantiates its clients."""
    # Clear registry before test
    _tool_registry.clear()
    
    class TestTool(BaseTool):
        async def execute(self, *args, **kwargs):
            return "test"
    
    tool = TestTool()
    
    # Verify client types
    assert isinstance(tool.searxng_client, SearxNGClient)
    assert isinstance(tool.firecrawl_client, FirecrawlClient)
    assert isinstance(tool.redis_client, RedisClient)
    
    # Verify they are different instances (not shared references)
    assert tool.searxng_client is not tool.firecrawl_client
    assert tool.searxng_client is not tool.redis_client
    assert tool.firecrawl_client is not tool.redis_client


@pytest.mark.asyncio
async def test_base_tool_execute_abstract_method():
    """Test that BaseTool execute method raises NotImplementedError."""
    # Clear registry before test
    _tool_registry.clear()
    
    class TestTool(BaseTool):
        pass  # No execute implementation
    
    tool = TestTool()
    
    # Should raise NotImplementedError when calling execute directly
    with pytest.raises(NotImplementedError):
        await tool.execute()


@pytest.mark.asyncio
async def test_base_tool_multiple_instantiations():
    """Test that multiple BaseTool instances work correctly."""
    # Clear registry before test
    _tool_registry.clear()
    
    class TestTool(BaseTool):
        async def execute(self, *args, **kwargs):
            return "test"
    
    # Create multiple instances
    tool1 = TestTool()
    tool2 = TestTool()
    
    # Verify they are different instances
    assert tool1 is not tool2
    assert tool1.searxng_client is not tool2.searxng_client
    assert tool1.firecrawl_client is not tool2.firecrawl_client
    assert tool1.redis_client is not tool2.redis_client


@pytest.mark.asyncio
async def test_base_tool_registry_cleanup():
    """Test that registry cleanup works properly."""
    # Clear registry before test
    _tool_registry.clear()
    
    class TestTool(BaseTool):
        tool_metadata = {
            "name": "cleanup_test_tool",
            "description": "A test tool for cleanup"
        }
        
        async def execute(self, *args, **kwargs):
            return "test"
    
    # Create and register tool
    tool = TestTool()
    
    # Verify registration
    assert "cleanup_test_tool" in _tool_registry
    
    # Clear registry manually to test cleanup
    _tool_registry.clear()
    
    # Verify registry is empty
    assert len(_tool_registry) == 0