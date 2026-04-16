"""
Base tool class for MCP Search Server tools.

Provides common functionality and structure for all MCP tools.
"""

import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

from mcp_search.core import settings
from mcp_search.clients import SearxNGClient, FirecrawlClient, RedisClient
from mcp_search.schemas import SearchRequest, ScrapeUrlRequest
from mcp_search.core.exceptions import SearchError, ScrapingError

logger = logging.getLogger(__name__)


# Global registry for tools
_tool_registry: Dict[str, 'BaseTool'] = {}


class BaseTool(ABC):
    """
    Base class for all MCP tools.
    
    Provides common functionality and structure for tool implementations.
    """

    tool_metadata: Dict[str, Any] = {
        "name": None,
        "description": None,
        "parameters": {}
    }

    def __init__(self):
        """Initialize base tool with required clients."""
        self.searxng_client = SearxNGClient()
        self.firecrawl_client = FirecrawlClient()
        self.redis_client = RedisClient()
        
        # Register this tool instance
        tool_name = getattr(self, 'tool_metadata', {}).get('name')
        if tool_name:
            _tool_registry[tool_name] = self
            
        logger.info(f"Base tool initialized and registered: {tool_name}")

    @abstractmethod
    async def execute(self, *args, **kwargs):
        """
        Execute the tool functionality.
        
        This method must be implemented by subclasses.
        
        Args:
            *args: Positional arguments for the tool
            **kwargs: Keyword arguments for the tool
            
        Returns:
            The result of the tool execution
        """
        pass

    async def close(self):
        """Close all client connections."""
        await self.searxng_client.close()
        await self.firecrawl_client.close()
        await self.redis_client.close()
        logger.info("Tool clients closed")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()