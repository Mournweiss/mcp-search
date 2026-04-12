"""
Unit tests for MCP Search base HTTP client.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from mcp_search.clients.base import BaseClient


@pytest.mark.asyncio
async def test_base_client_initialization():
    """Test BaseClient initialization."""
    client = BaseClient(base_url="http://test.example.com")
    
    assert client.base_url == "http://test.example.com"
    assert hasattr(client, 'client')
    assert client.client is not None


@pytest.mark.asyncio
async def test_base_client_with_none_base_url():
    """Test BaseClient initialization with None base URL."""
    client = BaseClient()
    
    assert client.base_url == ""
    assert hasattr(client, 'client')


@pytest.mark.asyncio
async def test_base_client_get_method():
    """Test BaseClient GET method."""
    # Mock the httpx.AsyncClient
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"test": "data"}
    
    with patch('mcp_search.clients.base.httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_instance.get.return_value = mock_response
        mock_client_class.return_value = mock_instance
        
        client = BaseClient(base_url="http://test.example.com")
        
        # Test GET request
        response = await client.get("/test-endpoint", params={"key": "value"})
        
        assert response == mock_response
        mock_instance.get.assert_called_once_with(
            "/test-endpoint",
            params={"key": "value"},
            headers=None
        )


@pytest.mark.asyncio
async def test_base_client_post_method():
    """Test BaseClient POST method."""
    # Mock the httpx.AsyncClient
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"test": "data"}
    
    with patch('mcp_search.clients.base.httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_instance
        
        client = BaseClient(base_url="http://test.example.com")
        
        # Test POST request
        response = await client.post(
            "/test-endpoint", 
            json_data={"key": "value"},
            headers={"Content-Type": "application/json"}
        )
        
        assert response == mock_response
        mock_instance.post.assert_called_once_with(
            "/test-endpoint",
            data=None,
            json_data={"key": "value"},
            headers={"Content-Type": "application/json"}
        )


@pytest.mark.asyncio
async def test_base_client_close():
    """Test BaseClient close method."""
    with patch('mcp_search.clients.base.httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_client_class.return_value = mock_instance
        
        client = BaseClient(base_url="http://test.example.com")
        
        # Test close
        await client.close()
        
        assert mock_instance.aclose.called


@pytest.mark.asyncio
async def test_base_client_context_manager():
    """Test BaseClient context manager."""
    with patch('mcp_search.clients.base.httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_client_class.return_value = mock_instance
        
        async with BaseClient(base_url="http://test.example.com") as client:
            pass
        
        # Should have called close when exiting context
        assert mock_instance.aclose.called


@pytest.mark.asyncio
async def test_base_client_error_handling():
    """Test BaseClient error handling."""
    with patch('mcp_search.clients.base.httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_instance.get.side_effect = Exception("Network error")
        mock_client_class.return_value = mock_instance
        
        client = BaseClient(base_url="http://test.example.com")
        
        # Test that exceptions are properly propagated
        with pytest.raises(Exception) as exc_info:
            await client.get("/test-endpoint")
        
        assert str(exc_info.value) == "Network error"