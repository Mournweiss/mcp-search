"""
Unit tests for MCP Search Redis client.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from mcp_search.clients.redis import RedisClient
from mcp_search.core.exceptions import CacheError


@pytest.mark.asyncio
async def test_redis_client_initialization():
    """Test RedisClient initialization."""
    client = RedisClient()
    
    assert hasattr(client, 'base_url')
    assert client.base_url == ""
    assert client.client is None


@pytest.mark.asyncio
async def test_redis_client_initialization_with_base_url():
    """Test RedisClient initialization with base URL."""
    client = RedisClient(base_url="redis://localhost:6379")
    
    assert client.base_url == "redis://localhost:6379"
    assert client.client is None


@pytest.mark.asyncio
async def test_redis_client_connect_success():
    """Test successful Redis client connection."""
    with patch('mcp_search.clients.redis.redis.from_url') as mock_from_url:
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_from_url.return_value = mock_redis
        
        client = RedisClient()
        
        # Test connect
        await client.connect()
        
        # Verify connection was established
        assert client.client is not None
        mock_from_url.assert_called_once()
        mock_redis.ping.assert_called_once()


@pytest.mark.asyncio
async def test_redis_client_connect_failure():
    """Test Redis client connection failure."""
    with patch('mcp_search.clients.redis.redis.from_url') as mock_from_url:
        mock_from_url.side_effect = Exception("Connection failed")
        
        client = RedisClient()
        
        # Test that CacheError is raised on connection failure
        with pytest.raises(CacheError):
            await client.connect()


@pytest.mark.asyncio
async def test_redis_client_get_success():
    """Test successful Redis get operation."""
    with patch('mcp_search.clients.redis.redis.from_url') as mock_from_url:
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = "test_value"
        mock_from_url.return_value = mock_redis
        
        client = RedisClient()
        
        # Connect first
        await client.connect()
        
        # Test get operation
        result = await client.get("test_key")
        
        assert result == "test_value"
        mock_redis.get.assert_called_once_with("test_key")


@pytest.mark.asyncio
async def test_redis_client_get_with_none_connection():
    """Test Redis get operation with None connection (should auto-connect)."""
    with patch('mcp_search.clients.redis.redis.from_url') as mock_from_url:
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = "test_value"
        mock_from_url.return_value = mock_redis
        
        client = RedisClient()
        
        # Test get operation without explicit connection
        result = await client.get("test_key")
        
        assert result == "test_value"
        # Should have auto-connected
        mock_from_url.assert_called_once()
        mock_redis.ping.assert_called_once()


@pytest.mark.asyncio
async def test_redis_client_get_failure():
    """Test Redis get operation failure."""
    with patch('mcp_search.clients.redis.redis.from_url') as mock_from_url:
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_redis.get.side_effect = Exception("Get failed")
        mock_from_url.return_value = mock_redis
        
        client = RedisClient()
        
        # Connect first
        await client.connect()
        
        # Test that CacheError is raised on get failure
        with pytest.raises(CacheError):
            await client.get("test_key")


@pytest.mark.asyncio
async def test_redis_client_set_success():
    """Test successful Redis set operation."""
    with patch('mcp_search.clients.redis.redis.from_url') as mock_from_url:
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_redis.set.return_value = True
        mock_from_url.return_value = mock_redis
        
        client = RedisClient()
        
        # Connect first
        await client.connect()
        
        # Test set operation
        result = await client.set("test_key", "test_value")
        
        assert result is True
        mock_redis.set.assert_called_once_with("test_key", "test_value")


@pytest.mark.asyncio
async def test_redis_client_set_with_expiry():
    """Test Redis set operation with expiration."""
    with patch('mcp_search.clients.redis.redis.from_url') as mock_from_url:
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_redis.set.return_value = True
        mock_from_url.return_value = mock_redis
        
        client = RedisClient()
        
        # Connect first
        await client.connect()
        
        # Test set operation with expiration
        result = await client.set("test_key", "test_value", expire=3600)
        
        assert result is True
        mock_redis.set.assert_called_once_with("test_key", "test_value", ex=3600)


@pytest.mark.asyncio
async def test_redis_client_set_failure():
    """Test Redis set operation failure."""
    with patch('mcp_search.clients.redis.redis.from_url') as mock_from_url:
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_redis.set.side_effect = Exception("Set failed")
        mock_from_url.return_value = mock_redis
        
        client = RedisClient()
        
        # Connect first
        await client.connect()
        
        # Test that CacheError is raised on set failure
        with pytest.raises(CacheError):
            await client.set("test_key", "test_value")


@pytest.mark.asyncio
async def test_redis_client_close():
    """Test RedisClient close method."""
    with patch('mcp_search.clients.redis.redis.from_url') as mock_from_url:
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_from_url.return_value = mock_redis
        
        client = RedisClient()
        
        # Connect first
        await client.connect()
        
        # Test close
        await client.close()
        
        # Should call redis close method
        assert mock_redis.close.called


@pytest.mark.asyncio
async def test_redis_client_context_manager():
    """Test RedisClient context manager."""
    with patch('mcp_search.clients.redis.redis.from_url') as mock_from_url:
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_from_url.return_value = mock_redis
        
        # Test context manager
        async with RedisClient() as client:
            assert client is not None
            assert client.client is not None
            
        # Should have called close when exiting context
        assert mock_redis.close.called


@pytest.mark.asyncio
async def test_redis_client_context_manager_connection_failure():
    """Test RedisClient context manager with connection failure."""
    with patch('mcp_search.clients.redis.redis.from_url') as mock_from_url:
        mock_from_url.side_effect = Exception("Connection failed")
        
        # Test that context manager handles connection failure gracefully
        with pytest.raises(CacheError):
            async with RedisClient() as client:
                pass  # Should not reach here


@pytest.mark.asyncio
async def test_redis_client_reconnect():
    """Test that RedisClient can reconnect after closing."""
    with patch('mcp_search.clients.redis.redis.from_url') as mock_from_url:
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_from_url.return_value = mock_redis
        
        client = RedisClient()
        
        # Connect and close
        await client.connect()
        await client.close()
        
        # Reconnect should work
        await client.connect()
        
        assert client.client is not None
        assert mock_from_url.call_count == 2  # Called twice: once for connect, once for reconnect