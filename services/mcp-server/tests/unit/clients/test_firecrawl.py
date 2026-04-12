"""
Unit tests for MCP Search Firecrawl client.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from mcp_search.clients.firecrawl import FirecrawlClient
from mcp_search.core.exceptions import ScrapingError


@pytest.mark.asyncio
async def test_firecrawl_client_initialization():
    """Test FirecrawlClient initialization."""
    client = FirecrawlClient()
    
    assert hasattr(client, 'base_url')
    assert client.base_url == "http://firecrawl:3000"  # Default from settings


@pytest.mark.asyncio
async def test_firecrawl_client_scrape_urls_success():
    """Test successful scrape_urls operation with multiple URLs."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "title": "Scraped Title",
        "content": "Scraped content",
        "rawContent": "Raw content",
        "links": ["http://example.com/link1", "http://example.com/link2"],
        "metadata": {"author": "Test Author"}
    }
    
    with patch('mcp_search.clients.firecrawl.httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_instance
        
        client = FirecrawlClient()
        
        # Test scrape_urls
        result = await client.scrape_urls([
            "http://example.com/test1",
            "http://example.com/test2"
        ], {"includeHtml": True})
        
        # Verify the calls were made correctly
        assert mock_instance.post.call_count == 2
        
        # Verify results structure
        assert len(result.results) == 2
        assert result.total_scraped == 2
        assert result.total_failed == 0
        assert result.failed_urls == []


@pytest.mark.asyncio
async def test_firecrawl_client_scrape_single_url_success():
    """Test successful single URL scraping."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "title": "Scraped Title",
        "content": "Scraped content",
        "rawContent": "Raw content",
        "links": ["http://example.com/link1"],
        "metadata": {"author": "Test Author"}
    }
    
    with patch('mcp_search.clients.firecrawl.httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_instance
        
        client = FirecrawlClient()
        
        # Test single URL scraping
        result = await client._scrape_single_url("http://example.com/test")
        
        # Verify the call was made correctly
        mock_instance.post.assert_called_once_with(
            "/scrape",
            json={
                "url": "http://example.com/test",
                "limit": 1000
            }
        )
        
        # Verify result structure
        assert result.url == "http://example.com/test"
        assert result.title == "Scraped Title"
        assert result.content == "Scraped content"
        assert result.raw_content == "Raw content"
        assert result.links == ["http://example.com/link1"]
        assert result.metadata == {"author": "Test Author"}
        assert result.source == "firecrawl"


@pytest.mark.asyncio
async def test_firecrawl_client_scrape_urls_with_failures():
    """Test scrape_urls with some failed URLs."""
    # Mock successful response for first URL, error for second
    mock_response1 = MagicMock()
    mock_response1.status_code = 200
    mock_response1.json.return_value = {
        "title": "Scraped Title 1",
        "content": "Scraped content 1"
    }
    
    mock_response2 = MagicMock()
    mock_response2.status_code = 500
    mock_response2.json.return_value = {"error": "Internal Server Error"}
    
    with patch('mcp_search.clients.firecrawl.httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_instance.post.side_effect = [mock_response1, mock_response2]
        mock_client_class.return_value = mock_instance
        
        client = FirecrawlClient()
        
        # Test scrape_urls with one failure
        result = await client.scrape_urls([
            "http://example.com/test1",
            "http://example.com/test2"
        ])
        
        # Verify results structure
        assert len(result.results) == 1  # Only successful scrape
        assert result.total_scraped == 1
        assert result.total_failed == 1
        assert len(result.failed_urls) == 1
        assert result.failed_urls[0] == "http://example.com/test2"


@pytest.mark.asyncio
async def test_firecrawl_client_scrape_network_error():
    """Test scrape with network error."""
    with patch('mcp_search.clients.firecrawl.httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_instance.post.side_effect = Exception("Network error")
        mock_client_class.return_value = mock_instance
        
        client = FirecrawlClient()
        
        # Test that ScrapingError is raised
        with pytest.raises(ScrapingError):
            await client.scrape_urls(["http://example.com/test"])


@pytest.mark.asyncio
async def test_firecrawl_client_scrape_http_error():
    """Test scrape with HTTP error response."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"error": "Internal Server Error"}
    
    with patch('mcp_search.clients.firecrawl.httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_instance
        
        client = FirecrawlClient()
        
        # Test that ScrapingError is raised for HTTP error
        with pytest.raises(ScrapingError):
            await client._scrape_single_url("http://example.com/test")


@pytest.mark.asyncio
async def test_firecrawl_client_scrape_empty_urls():
    """Test scrape_urls with empty URL list."""
    client = FirecrawlClient()
    
    # Should not make any calls and return empty results
    result = await client.scrape_urls([])
    
    assert len(result.results) == 0
    assert result.total_scraped == 0
    assert result.total_failed == 0
    assert result.failed_urls == []


@pytest.mark.asyncio
async def test_firecrawl_client_close():
    """Test FirecrawlClient close method."""
    with patch('mcp_search.clients.firecrawl.httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_client_class.return_value = mock_instance
        
        client = FirecrawlClient()
        
        # Test close
        await client.close()
        
        # Should call parent's close method
        assert mock_instance.aclose.called


@pytest.mark.asyncio
async def test_firecrawl_client_scrape_with_options():
    """Test scrape with additional options."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "title": "Scraped Title",
        "content": "Scraped content"
    }
    
    with patch('mcp_search.clients.firecrawl.httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_instance
        
        client = FirecrawlClient()
        
        # Test scrape with options
        result = await client.scrape_urls(
            ["http://example.com/test"],
            {"includeHtml": True, "includeLinks": False, "limit": 500}
        )
        
        # Verify the call included options
        call_args = mock_instance.post.call_args
        assert call_args[1]['json']['url'] == "http://example.com/test"
        assert call_args[1]['json']['limit'] == 500