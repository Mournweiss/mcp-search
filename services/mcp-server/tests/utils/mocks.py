"""
Mock objects for MCP Search tests.
"""

from unittest.mock import MagicMock
from mcp_search.clients.base import BaseClient
from mcp_search.clients.searxng import SearxNGClient
from mcp_search.clients.firecrawl import FirecrawlClient
from mcp_search.server.tools import MCPTools


class MockBaseClient(BaseClient):
    """Mock BaseClient for testing."""
    
    def __init__(self, base_url="http://mock.example.com"):
        super().__init__(base_url)
        # Override the client with a mock
        self.client = MagicMock()


class MockSearxNGClient(SearxNGClient):
    """Mock SearxNGClient for testing."""
    
    def __init__(self):
        super().__init__()
        # Override the client with a mock
        self.client = MagicMock()
    
    async def search(self, query: str, max_results: int = 10):
        """Mock search method."""
        # Return a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "title": f"Mock Result for {query}",
                    "url": f"http://example.com/{query}",
                    "content": f"Content for {query}",
                    "score": 0.8,
                    "category": "general"
                }
            ]
        }
        return mock_response


class MockFirecrawlClient(FirecrawlClient):
    """Mock FirecrawlClient for testing."""
    
    def __init__(self):
        super().__init__()
        # Override the client with a mock
        self.client = MagicMock()
    
    async def scrape_urls(self, urls: list, options=None):
        """Mock scrape_urls method."""
        # Return a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Mock Scraped Title",
            "content": "Mock scraped content",
            "rawContent": "Mock raw content",
            "links": ["http://example.com/link1"],
            "metadata": {"author": "Mock Author"}
        }
        return mock_response


class MockMCPTools(MCPTools):
    """Mock MCPTools for testing."""
    
    def __init__(self):
        super().__init__()
        # Replace clients with mocks
        self.searxng_client = MockSearxNGClient()
        self.firecrawl_client = MockFirecrawlClient()
        self.redis_client = MagicMock()