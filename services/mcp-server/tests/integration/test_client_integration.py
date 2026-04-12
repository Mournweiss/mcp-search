"""
Integration tests for MCP Search Server client components.
"""

import pytest
import asyncio


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


@pytest.mark.asyncio
async def test_client_context_managers():
    """Test that all clients work properly with context managers."""
    from mcp_search.clients.searxng import SearxNGClient
    from mcp_search.clients.firecrawl import FirecrawlClient
    
    # Test SearxNG client context manager
    async with SearxNGClient() as searxng_client:
        assert searxng_client is not None
    
    # Test Firecrawl client context manager  
    async with FirecrawlClient() as firecrawl_client:
        assert firecrawl_client is not None


# This file can be expanded with actual integration tests
# that test real HTTP calls or database interactions when needed