"""
Unit tests for MCP Search SearxNG client.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from mcp_search.clients.searxng import SearxNGClient
from mcp_search.core.exceptions import SearchError


@pytest.mark.asyncio
async def test_searxng_client_initialization():
    """Test SearxNGClient initialization."""
    client = SearxNGClient()
    
    assert hasattr(client, 'base_url')
    assert client.base_url == "http://searxng:8080"  # Default from settings


@pytest.mark.asyncio
async def test_searxng_client_search_success():
    """Test successful search operation."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "title": "Test Result 1",
                "url": "http://example.com/test1",
                "content": "Test content 1",
                "score": 0.9,
                "category": "general"
            },
            {
                "title": "Test Result 2", 
                "url": "http://example.com/test2",
                "content": "Test content 2",
                "score": 0.8,
                "category": "technology"
            }
        ]
    }
    
    with patch('mcp_search.clients.searxng.httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_instance.get.return_value = mock_response
        mock_client_class.return_value = mock_instance
        
        client = SearxNGClient()
        
        # Test search
        result = await client.search("test query", 5)
        
        # Verify the call was made correctly
        mock_instance.get.assert_called_once_with(
            "/search",
            params={
                "q": "test query",
                "format": "json",
                "limit": 5
            }
        )
        
        # Verify results structure
        assert len(result.results) == 2
        assert result.total_results == 2
        assert result.query == "test query"
        assert result.search_type == "general"


@pytest.mark.asyncio
async def test_searxng_client_search_empty_results():
    """Test search with empty results."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": []}
    
    with patch('mcp_search.clients.searxng.httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_instance.get.return_value = mock_response
        mock_client_class.return_value = mock_instance
        
        client = SearxNGClient()
        
        # Test search
        result = await client.search("test query", 5)
        
        # Verify results structure
        assert len(result.results) == 0
        assert result.total_results == 0
        assert result.query == "test query"


@pytest.mark.asyncio
async def test_searxng_client_search_http_error():
    """Test search with HTTP error response."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"error": "Internal Server Error"}
    
    with patch('mcp_search.clients.searxng.httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_instance.get.return_value = mock_response
        mock_client_class.return_value = mock_instance
        
        client = SearxNGClient()
        
        # Test that SearchError is raised
        with pytest.raises(SearchError):
            await client.search("test query", 5)


@pytest.mark.asyncio
async def test_searxng_client_search_network_error():
    """Test search with network error."""
    with patch('mcp_search.clients.searxng.httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_instance.get.side_effect = Exception("Network error")
        mock_client_class.return_value = mock_instance
        
        client = SearxNGClient()
        
        # Test that SearchError is raised
        with pytest.raises(SearchError):
            await client.search("test query", 5)


@pytest.mark.asyncio
async def test_searxng_client_search_missing_fields():
    """Test search with partial result data."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "title": "Test Result 1",
                # Missing url, content, score, category
            }
        ]
    }
    
    with patch('mcp_search.clients.searxng.httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_instance.get.return_value = mock_response
        mock_client_class.return_value = mock_instance
        
        client = SearxNGClient()
        
        # Test search - should not raise exception, but fields will be empty
        result = await client.search("test query", 5)
        
        assert len(result.results) == 1
        assert result.results[0].title == "Test Result 1"
        assert result.results[0].url == ""
        assert result.results[0].content == ""
        assert result.results[0].score is None
        assert result.results[0].category is None


@pytest.mark.asyncio
async def test_searxng_client_close():
    """Test SearxNGClient close method."""
    with patch('mcp_search.clients.searxng.httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_client_class.return_value = mock_instance
        
        client = SearxNGClient()
        
        # Test close
        await client.close()
        
        # Should call parent's close method
        assert mock_instance.aclose.called