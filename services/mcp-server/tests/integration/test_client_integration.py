"""
Integration tests for MCP Search Server client components.
"""

import pytest
import asyncio
from mcp_search.clients import SearxNGClient, FirecrawlClient, RedisClient


@pytest.mark.asyncio
async def test_client_initialization():
    """Test that all clients can be initialized properly."""
    # Import and test initialization of all clients
    from mcp_search.clients.searxng import SearxNGClient
    from mcp_search.clients.firecrawl import FirecrawlClient
    from mcp_search.clients.base import BaseClient
    
    # Test base client
    base_client = BaseClient()
    assert base_client is not None
    
    # Test SearxNG client
    searxng_client = SearxNGClient()
    assert searxng_client is not None
    
    # Test Firecrawl client
    firecrawl_client = FirecrawlClient()
    assert firecrawl_client is not None
    
    # Test Redis client
    redis_client = RedisClient()
    assert redis_client is not None


@pytest.mark.asyncio
async def test_client_context_managers():
    """Test that all clients work properly with context managers."""
    from mcp_search.clients.searxng import SearxNGClient
    from mcp_search.clients.firecrawl import FirecrawlClient
    from mcp_search.clients.redis import RedisClient
    
    # Test SearxNG client context manager
    async with SearxNGClient() as searxng_client:
        assert searxng_client is not None
    
    # Test Firecrawl client context manager  
    async with FirecrawlClient() as firecrawl_client:
        assert firecrawl_client is not None
        
    # Test Redis client context manager
    async with RedisClient() as redis_client:
        assert redis_client is not None


@pytest.mark.asyncio
async def test_client_base_url_handling():
    """Test that clients handle base URLs correctly."""
    # Test with custom base URL
    searxng_client = SearxNGClient(base_url="http://custom-searxng:8080")
    firecrawl_client = FirecrawlClient(base_url="http://custom-firecrawl:3000")
    
    assert searxng_client.base_url == "http://custom-searxng:8080"
    assert firecrawl_client.base_url == "http://custom-firecrawl:3000"


@pytest.mark.asyncio
async def test_client_inheritance():
    """Test that clients properly inherit from BaseClient."""
    from mcp_search.clients.base import BaseClient
    
    searxng_client = SearxNGClient()
    firecrawl_client = FirecrawlClient()
    redis_client = RedisClient()
    
    assert isinstance(searxng_client, BaseClient)
    assert isinstance(firecrawl_client, BaseClient)
    assert isinstance(redis_client, BaseClient)


@pytest.mark.asyncio
async def test_client_method_signatures():
    """Test that client methods have correct signatures."""
    searxng_client = SearxNGClient()
    firecrawl_client = FirecrawlClient()
    redis_client = RedisClient()
    
    # Test that all clients have expected methods
    assert hasattr(searxng_client, 'get')
    assert hasattr(searxng_client, 'post')
    assert hasattr(searxng_client, 'close')
    
    assert hasattr(firecrawl_client, 'get')
    assert hasattr(firecrawl_client, 'post')
    assert hasattr(firecrawl_client, 'close')
    
    assert hasattr(redis_client, 'get')
    assert hasattr(redis_client, 'set')
    assert hasattr(redis_client, 'close')


@pytest.mark.asyncio
async def test_client_module_imports():
    """Test that all client modules can be imported correctly."""
    # Test importing all client classes from the main module
    from mcp_search.clients import (
        BaseClient,
        SearxNGClient,
        FirecrawlClient,
        RedisClient
    )
    
    # Verify all imports worked
    assert BaseClient is not None
    assert SearxNGClient is not None
    assert FirecrawlClient is not None
    assert RedisClient is not None
    
    # Test that we can create instances
    base_client = BaseClient()
    searxng_client = SearxNGClient()
    firecrawl_client = FirecrawlClient()
    redis_client = RedisClient()
    
    assert base_client is not None
    assert searxng_client is not None
    assert firecrawl_client is not None
    assert redis_client is not None