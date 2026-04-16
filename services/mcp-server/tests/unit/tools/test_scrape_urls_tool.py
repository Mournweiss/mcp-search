"""
Unit tests for MCP Scrape URLs Tool.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from mcp_search.tools.scrape_urls import ScrapeUrlsTool
from mcp_search.core.exceptions import ToolExecutionError
from mcp_search.schemas import ScrapeUrlRequest


@pytest.mark.asyncio
async def test_scrape_urls_tool_initialization():
    """Test ScrapeUrlsTool initialization."""
    tool = ScrapeUrlsTool()
    
    assert tool is not None
    assert hasattr(tool, 'tool_metadata')
    assert tool.tool_metadata["name"] == "scrape_urls"
    assert tool.tool_metadata["description"] == "Scrape one or more URLs using Firecrawl."
    assert "urls" in tool.tool_metadata["parameters"]
    assert "options" in tool.tool_metadata["parameters"]


@pytest.mark.asyncio
async def test_scrape_urls_tool_execute_success():
    """Test ScrapeUrlsTool execute method with successful scraping."""
    tool = ScrapeUrlsTool()
    
    # Mock the Firecrawl client scrape_urls method
    mock_scrape_response = MagicMock()
    mock_scrape_response.model_dump_json.return_value = '{"scraped": ["test"]}'
    
    with patch.object(tool.firecrawl_client, 'scrape_urls', new_callable=AsyncMock) as mock_scrape:
        mock_scrape.return_value = mock_scrape_response
        
        # Test execute method
        result = await tool.execute(["http://example.com"], {"includeHtml": True})
        
        # Verify the result is a string (JSON)
        assert isinstance(result, str)
        assert "scraped" in result
        
        # Verify scrape was called with correct parameters
        mock_scrape.assert_called_once_with(["http://example.com"], {"includeHtml": True})


@pytest.mark.asyncio
async def test_scrape_urls_tool_execute_empty_urls():
    """Test ScrapeUrlsTool execute method with empty URL list."""
    tool = ScrapeUrlsTool()
    
    # Test with empty URL list
    result = await tool.execute([], {"includeHtml": True})
    
    # Should return error message string
    assert isinstance(result, str)
    assert "Scraping failed" in result or "empty" in result.lower()


@pytest.mark.asyncio
async def test_scrape_urls_tool_execute_none_urls():
    """Test ScrapeUrlsTool execute method with None URL list."""
    tool = ScrapeUrlsTool()
    
    # Test with None URL list
    result = await tool.execute(None, {"includeHtml": True})
    
    # Should return error message string
    assert isinstance(result, str)
    assert "Scraping failed" in result or "empty" in result.lower()


@pytest.mark.asyncio
async def test_scrape_urls_tool_execute_with_defaults():
    """Test ScrapeUrlsTool execute method with default parameters."""
    tool = ScrapeUrlsTool()
    
    # Mock the Firecrawl client scrape_urls method
    mock_scrape_response = MagicMock()
    mock_scrape_response.model_dump_json.return_value = '{"scraped": ["test"]}'
    
    with patch.object(tool.firecrawl_client, 'scrape_urls', new_callable=AsyncMock) as mock_scrape:
        mock_scrape.return_value = mock_scrape_response
        
        # Test execute method without options (should work)
        result = await tool.execute(["http://example.com"])
        
        # Verify the result is a string (JSON)
        assert isinstance(result, str)
        assert "scraped" in result
        
        # Verify scrape was called with correct parameters
        mock_scrape.assert_called_once_with(["http://example.com"], None)


@pytest.mark.asyncio
async def test_scrape_urls_tool_execute_scraping_error():
    """Test ScrapeUrlsTool execute method when scraping raises ScrapingError."""
    tool = ScrapeUrlsTool()
    
    # Mock the Firecrawl client to raise a ScrapingError
    with patch.object(tool.firecrawl_client, 'scrape_urls', new_callable=AsyncMock) as mock_scrape:
        from mcp_search.core import ScrapingError
        mock_scrape.side_effect = ScrapingError("Scraping failed")
        
        # Test execute method
        result = await tool.execute(["http://example.com"], {"includeHtml": True})
        
        # Should return error message string
        assert isinstance(result, str)
        assert "Scraping failed" in result


@pytest.mark.asyncio
async def test_scrape_urls_tool_execute_unexpected_error():
    """Test ScrapeUrlsTool execute method when unexpected error occurs."""
    tool = ScrapeUrlsTool()
    
    # Mock the Firecrawl client to raise an unexpected exception
    with patch.object(tool.firecrawl_client, 'scrape_urls', new_callable=AsyncMock) as mock_scrape:
        mock_scrape.side_effect = Exception("Unexpected error")
        
        # Test execute method - should raise ToolExecutionError
        with pytest.raises(ToolExecutionError):
            await tool.execute(["http://example.com"], {"includeHtml": True})


@pytest.mark.asyncio
async def test_scrape_urls_tool_execute_parameter_validation():
    """Test ScrapeUrlsTool execute method parameter validation."""
    tool = ScrapeUrlsTool()
    
    # Test with various parameter combinations
    test_cases = [
        (["http://example.com"], {"includeHtml": True}),
        (["http://example.com", "http://test.com"], None),
        ([], {"includeHtml": True}),  # Empty URL list
        (None, {"includeHtml": True}),  # None URL list
    ]
    
    for urls, options in test_cases:
        if urls is None or len(urls) == 0:
            # These should return error strings rather than raise exceptions
            result = await tool.execute(urls, options)
            assert isinstance(result, str)
        else:
            # These should work normally (mocked)
            mock_scrape_response = MagicMock()
            mock_scrape_response.model_dump_json.return_value = '{"scraped": ["test"]}'
            
            with patch.object(tool.firecrawl_client, 'scrape_urls', new_callable=AsyncMock) as mock_scrape:
                mock_scrape.return_value = mock_scrape_response
                result = await tool.execute(urls, options)
                assert isinstance(result, str)


@pytest.mark.asyncio
async def test_scrape_urls_tool_execute_multiple_urls():
    """Test ScrapeUrlsTool execute method with multiple URLs."""
    tool = ScrapeUrlsTool()
    
    # Mock the Firecrawl client scrape_urls method
    mock_scrape_response = MagicMock()
    mock_scrape_response.model_dump_json.return_value = '{"scraped": ["test1", "test2"]}'
    
    with patch.object(tool.firecrawl_client, 'scrape_urls', new_callable=AsyncMock) as mock_scrape:
        mock_scrape.return_value = mock_scrape_response
        
        # Test execute method with multiple URLs
        result = await tool.execute([
            "http://example.com", 
            "http://test.com",
            "http://demo.com"
        ], {"includeHtml": True})
        
        # Verify the result is a string (JSON)
        assert isinstance(result, str)
        assert "scraped" in result
        
        # Verify scrape was called with correct parameters
        mock_scrape.assert_called_once()


@pytest.mark.asyncio
async def test_scrape_urls_tool_execute_client_integration():
    """Test ScrapeUrlsTool execute method client integration."""
    tool = ScrapeUrlsTool()
    
    # Verify that the tool has the expected clients
    assert hasattr(tool, 'searxng_client')
    assert hasattr(tool, 'firecrawl_client')
    assert hasattr(tool, 'redis_client')
    
    # Mock the scrape method to verify it's called on the correct client
    mock_scrape_response = MagicMock()
    mock_scrape_response.model_dump_json.return_value = '{"scraped": ["test"]}'
    
    with patch.object(tool.firecrawl_client, 'scrape_urls', new_callable=AsyncMock) as mock_scrape:
        mock_scrape.return_value = mock_scrape_response
        
        # Execute the tool
        result = await tool.execute(["http://example.com"], {"includeHtml": True})
        
        # Verify that scrape was called on the firecrawl client
        assert mock_scrape.called
        mock_scrape.assert_called_once_with(["http://example.com"], {"includeHtml": True})


@pytest.mark.asyncio
async def test_scrape_urls_tool_execute_options_handling():
    """Test ScrapeUrlsTool execute method with various options handling."""
    tool = ScrapeUrlsTool()
    
    # Test with different option formats
    test_options = [
        None,
        {},
        {"includeHtml": True},
        {"includeMarkdown": False, "includeRawHtml": True},
        {"timeout": 30, "headers": {"User-Agent": "test"}},
    ]
    
    for options in test_options:
        # Mock the Firecrawl client scrape_urls method
        mock_scrape_response = MagicMock()
        mock_scrape_response.model_dump_json.return_value = '{"scraped": ["test"]}'
        
        with patch.object(tool.firecrawl_client, 'scrape_urls', new_callable=AsyncMock) as mock_scrape:
            mock_scrape.return_value = mock_scrape_response
            
            # Execute the tool
            result = await tool.execute(["http://example.com"], options)
            
            # Verify the result is a string (JSON)
            assert isinstance(result, str)
            
            # Verify scrape was called with correct parameters
            mock_scrape.assert_called_once()