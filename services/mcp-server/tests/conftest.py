"""
Shared test fixtures for MCP Search tests.

Provides common fixtures and configuration for all test modules.
"""

import asyncio
import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'mcp-server', 'src'))

from mcp_search.core.config import settings
from mcp_search.clients.templates import BaseClient
from mcp_search.clients.searxng import SearxNGClient
from mcp_search.clients.firecrawl import FirecrawlClient
from mcp_search.tools.registry import ToolRegistry


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def mock_settings():
    """Provide a clean settings object for testing."""
    # Reset to defaults before each test
    return settings


@pytest.fixture(scope="function")
def base_client():
    """Create a BaseClient instance for testing."""
    return BaseClient(base_url="http://test.example.com")


@pytest.fixture(scope="function")
def searxng_client():
    """Create a SearxNGClient instance for testing."""
    return SearxNGClient()


@pytest.fixture(scope="function")
def firecrawl_client():
    """Create a FirecrawlClient instance for testing."""
    return FirecrawlClient()


@pytest.fixture(scope="function")
def tool_registry():
    """Create a ToolRegistry instance for testing."""
    return ToolRegistry()


@pytest.fixture(scope="function")
def test_search_request():
    """Provide a sample search request for testing."""
    from mcp_search.schemas.search import SearchRequest
    
    return SearchRequest(
        query="test query",
        search_type="general",
        max_results=10
    )


@pytest.fixture(scope="function")
def test_search_result():
    """Provide a sample search result for testing."""
    from mcp_search.schemas.search import SearchResult
    
    return SearchResult(
        title="Test Title",
        url="http://example.com/test",
        content="Test content for the search result",
        source="searxng",
        score=0.8,
        category="general"
    )


@pytest.fixture(scope="function")
def test_search_response():
    """Provide a sample search response for testing."""
    from mcp_search.schemas.search import SearchResponse
    
    return SearchResponse(
        results=[],
        total_results=0,
        query="test query",
        search_type="general"
    )


@pytest.fixture(scope="function")
def test_scrape_request():
    """Provide a sample scrape request for testing."""
    from mcp_search.schemas.scrape import ScrapeUrlRequest
    
    return ScrapeUrlRequest(
        urls=["http://example.com/test1", "http://example.com/test2"],
        options={"includeHtml": True}
    )


@pytest.fixture(scope="function")
def test_scraping_result():
    """Provide a sample scraping result for testing."""
    from mcp_search.schemas.scrape import ScrapingResult
    
    return ScrapingResult(
        url="http://example.com/test",
        title="Test Title",
        content="Test content for the scraped page",
        raw_content="<html><body>Raw content</body></html>",
        links=["http://example.com/link1", "http://example.com/link2"],
        metadata={"author": "Test Author"},
        source="firecrawl"
    )


@pytest.fixture(scope="function")
def test_scrape_response():
    """Provide a sample scrape response for testing."""
    from mcp_search.schemas.scrape import ScrapeResponse
    
    return ScrapeResponse(
        results=[],
        total_scraped=0,
        total_failed=0,
        failed_urls=[]
    )