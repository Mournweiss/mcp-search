"""
Unit tests for MCP Search tools.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from mcp_search.server.tools import MCPTools
from mcp_search.core.exceptions import SearchError, ScrapingError
from mcp.types import ToolCall, ToolResult, TextContent


@pytest.mark.asyncio
async def test_mcp_tools_initialization():
    """Test MCPTools initialization."""
    tools = MCPTools()
    
    assert hasattr(tools, 'searxng_client')
    assert hasattr(tools, 'firecrawl_client')
    assert hasattr(tools, 'redis_client')


@pytest.mark.asyncio
async def test_search_web_success():
    """Test successful search_web tool call."""
    # Mock the SearxNG client response
    mock_search_response = MagicMock()
    mock_search_response.results = [
        MagicMock(
            title="Test Result 1",
            url="http://example.com/test1",
            content="Test content 1",
            source="searxng",
            score=0.9,
            category="general"
        )
    ]
    mock_search_response.total_results = 1
    mock_search_response.query = "test query"
    mock_search_response.search_type = "general"
    
    with patch.object(MCPTools, 'searxng_client') as mock_searxng:
        mock_searxng.search.return_value = mock_search_response
        
        tools = MCPTools()
        
        # Create a mock tool call
        tool_call = MagicMock()
        tool_call.name = "search_web"
        tool_call.arguments = MagicMock()
        tool_call.arguments.dict.return_value = {
            "query": "test query",
            "max_results": 5
        }
        
        # Test search_web method
        result = await tools.search_web(tool_call)
        
        # Verify result structure
        assert isinstance(result, ToolResult)
        assert result.isError is False
        assert len(result.contents) == 1
        assert isinstance(result.contents[0], TextContent)


@pytest.mark.asyncio
async def test_search_web_empty_query():
    """Test search_web with empty query."""
    tools = MCPTools()
    
    # Create a mock tool call with empty query
    tool_call = MagicMock()
    tool_call.name = "search_web"
    tool_call.arguments = MagicMock()
    tool_call.arguments.dict.return_value = {
        "query": "",
        "max_results": 5
    }
    
    # Test that SearchError is raised
    result = await tools.search_web(tool_call)
    
    assert result.isError is True
    assert len(result.contents) == 1
    assert isinstance(result.contents[0], TextContent)
    assert "Search failed" in result.contents[0].text


@pytest.mark.asyncio
async def test_search_web_search_error():
    """Test search_web when SearxNG client raises SearchError."""
    with patch.object(MCPTools, 'searxng_client') as mock_searxng:
        mock_searxng.search.side_effect = SearchError("Search failed")
        
        tools = MCPTools()
        
        # Create a mock tool call
        tool_call = MagicMock()
        tool_call.name = "search_web"
        tool_call.arguments = MagicMock()
        tool_call.arguments.dict.return_value = {
            "query": "test query",
            "max_results": 5
        }
        
        # Test that error is handled properly
        result = await tools.search_web(tool_call)
        
        assert result.isError is True
        assert len(result.contents) == 1
        assert isinstance(result.contents[0], TextContent)
        assert "Search failed" in result.contents[0].text


@pytest.mark.asyncio
async def test_search_web_unexpected_error():
    """Test search_web when unexpected error occurs."""
    with patch.object(MCPTools, 'searxng_client') as mock_searxng:
        mock_searxng.search.side_effect = Exception("Unexpected error")
        
        tools = MCPTools()
        
        # Create a mock tool call
        tool_call = MagicMock()
        tool_call.name = "search_web"
        tool_call.arguments = MagicMock()
        tool_call.arguments.dict.return_value = {
            "query": "test query",
            "max_results": 5
        }
        
        # Test that error is handled properly
        result = await tools.search_web(tool_call)
        
        assert result.isError is True
        assert len(result.contents) == 1
        assert isinstance(result.contents[0], TextContent)
        assert "Unexpected error" in result.contents[0].text


@pytest.mark.asyncio
async def test_scrape_urls_success():
    """Test successful scrape_urls tool call."""
    # Mock the Firecrawl client response
    mock_scrape_response = MagicMock()
    mock_scrape_response.results = [
        MagicMock(
            url="http://example.com/test1",
            title="Test Title 1",
            content="Test content 1",
            raw_content="Raw content 1",
            links=["http://example.com/link1"],
            metadata={"author": "Test Author"},
            source="firecrawl"
        )
    ]
    mock_scrape_response.total_scraped = 1
    mock_scrape_response.total_failed = 0
    mock_scrape_response.failed_urls = []
    
    with patch.object(MCPTools, 'firecrawl_client') as mock_firecrawl:
        mock_firecrawl.scrape_urls.return_value = mock_scrape_response
        
        tools = MCPTools()
        
        # Create a mock tool call
        tool_call = MagicMock()
        tool_call.name = "scrape_urls"
        tool_call.arguments = MagicMock()
        tool_call.arguments.dict.return_value = {
            "urls": ["http://example.com/test1"],
            "options": {"includeHtml": True}
        }
        
        # Test scrape_urls method
        result = await tools.scrape_urls(tool_call)
        
        # Verify result structure
        assert isinstance(result, ToolResult)
        assert result.isError is False
        assert len(result.contents) == 1
        assert isinstance(result.contents[0], TextContent)


@pytest.mark.asyncio
async def test_scrape_urls_empty_urls():
    """Test scrape_urls with empty URL list."""
    tools = MCPTools()
    
    # Create a mock tool call with empty URLs
    tool_call = MagicMock()
    tool_call.name = "scrape_urls"
    tool_call.arguments = MagicMock()
    tool_call.arguments.dict.return_value = {
        "urls": [],
        "options": None
    }
    
    # Test that ScrapingError is raised
    result = await tools.scrape_urls(tool_call)
    
    assert result.isError is True
    assert len(result.contents) == 1
    assert isinstance(result.contents[0], TextContent)
    assert "Scraping failed" in result.contents[0].text


@pytest.mark.asyncio
async def test_scrape_urls_scraping_error():
    """Test scrape_urls when Firecrawl client raises ScrapingError."""
    with patch.object(MCPTools, 'firecrawl_client') as mock_firecrawl:
        mock_firecrawl.scrape_urls.side_effect = ScrapingError("Scraping failed")
        
        tools = MCPTools()
        
        # Create a mock tool call
        tool_call = MagicMock()
        tool_call.name = "scrape_urls"
        tool_call.arguments = MagicMock()
        tool_call.arguments.dict.return_value = {
            "urls": ["http://example.com/test"],
            "options": None
        }
        
        # Test that error is handled properly
        result = await tools.scrape_urls(tool_call)
        
        assert result.isError is True
        assert len(result.contents) == 1
        assert isinstance(result.contents[0], TextContent)
        assert "Scraping failed" in result.contents[0].text


@pytest.mark.asyncio
async def test_scrape_urls_unexpected_error():
    """Test scrape_urls when unexpected error occurs."""
    with patch.object(MCPTools, 'firecrawl_client') as mock_firecrawl:
        mock_firecrawl.scrape_urls.side_effect = Exception("Unexpected error")
        
        tools = MCPTools()
        
        # Create a mock tool call
        tool_call = MagicMock()
        tool_call.name = "scrape_urls"
        tool_call.arguments = MagicMock()
        tool_call.arguments.dict.return_value = {
            "urls": ["http://example.com/test"],
            "options": None
        }
        
        # Test that error is handled properly
        result = await tools.scrape_urls(tool_call)
        
        assert result.isError is True
        assert len(result.contents) == 1
        assert isinstance(result.contents[0], TextContent)
        assert "Unexpected error" in result.contents[0].text


@pytest.mark.asyncio
async def test_close_method():
    """Test MCPTools close method."""
    tools = MCPTools()
    
    # Mock the client close methods
    with patch.object(tools.searxng_client, 'close') as mock_searxng_close, \
         patch.object(tools.firecrawl_client, 'close') as mock_firecrawl_close, \
         patch.object(tools.redis_client, 'close') as mock_redis_close:
        
        # Test close
        await tools.close()
        
        # Verify all clients were closed
        assert mock_searxng_close.called
        assert mock_firecrawl_close.called
        assert mock_redis_close.called


@pytest.mark.asyncio
async def test_context_manager():
    """Test MCPTools context manager."""
    tools = MCPTools()
    
    # Mock the client close methods
    with patch.object(tools.searxng_client, 'close') as mock_searxng_close, \
         patch.object(tools.firecrawl_client, 'close') as mock_firecrawl_close, \
         patch.object(tools.redis_client, 'close') as mock_redis_close:
        
        # Test context manager
        async with tools as t:
            assert t is tools
        
        # Verify all clients were closed when exiting context
        assert mock_searxng_close.called
        assert mock_firecrawl_close.called
        assert mock_redis_close.called