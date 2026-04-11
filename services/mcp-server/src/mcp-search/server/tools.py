"""
MCP tools for MCP Search Server.

Contains the implementation of MCP methods that will be exposed
to LLMs, including search_web and scrape_urls.
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from mcp.types import ToolCall, ToolResult, ToolResultContent, TextContent
from ..clients import (
    SearxNGClient,
    FirecrawlClient,
    RedisClient
)
from ..schemas import (
    SearchRequest,
    SearchResponse,
    ScrapeUrlRequest,
    ScrapeResponse
)
from ..core import (
    settings,
    SearchError,
    ScrapingError,
    CacheError
)


logger = logging.getLogger(__name__)


class MCPTools:
    """
    Handler class for MCP methods.
    
    Contains the implementations of the search_web and scrape_urls
    MCP methods that will be called by the MCP server.
    """
    
    def __init__(self):
        """Initialize MCP tools with necessary clients."""
        self.searxng_client = SearxNGClient()
        self.firecrawl_client = FirecrawlClient()
        self.redis_client = RedisClient()
        logger.info("MCP tools initialized")
        
    async def search_web(self, tool_call: ToolCall) -> ToolResult:
        """
        Handle the search_web MCP tool call.
        
        Performs a web search using SearxNG and returns structured results.
        
        Args:
            tool_call (ToolCall): The MCP tool call containing search parameters
            
        Returns:
            ToolResult: Structured result for the MCP client
        """
        logger.info(f"Handling search_web tool call: {tool_call.name}")
        
        try:
            # Extract parameters from tool call
            query = ""
            max_results = settings.default_max_results
            
            if tool_call.arguments:
                args = tool_call.arguments.dict() if hasattr(tool_call.arguments, 'dict') else tool_call.arguments
                query = args.get("query", "")
                max_results = args.get("max_results", settings.default_max_results)
            
            # Validate input
            if not query:
                raise SearchError("Search query cannot be empty")
                
            # Limit max_results to prevent abuse
            max_results = min(max_results, settings.max_search_results)
            
            # Perform search
            search_request = SearchRequest(query=query, max_results=max_results)
            search_response = await self.searxng_client.search(
                search_request.query,
                search_request.max_results
            )
            
            # Format results for MCP
            content: list[ToolResultContent] = []
            if search_response.results:
                result_text = search_response.json(indent=2)
                content.append(TextContent(type="text", text=result_text))
            
            return ToolResult(
                contents=content,
                isError=False
            )
            
        except SearchError as e:
            logger.error(f"Search error in search_web: {str(e)}")
            return ToolResult(
                contents=[TextContent(type="text", text=f"Search failed: {str(e)}")],
                isError=True
            )
        except Exception as e:
            logger.error(f"Unexpected error in search_web: {str(e)}")
            return ToolResult(
                contents=[TextContent(type="text", text=f"Unexpected error: {str(e)}")],
                isError=True
            )
            
    async def scrape_urls(self, tool_call: ToolCall) -> ToolResult:
        """
        Handle the scrape_urls MCP tool call.
        
        Scrapes multiple URLs using Firecrawl and returns structured results.
        
        Args:
            tool_call (ToolCall): The MCP tool call containing URL list
            
        Returns:
            ToolResult: Structured result for the MCP client
        """
        logger.info(f"Handling scrape_urls tool call: {tool_call.name}")
        
        try:
            # Extract parameters from tool call
            urls = []
            options = None
            
            if tool_call.arguments:
                args = tool_call.arguments.dict() if hasattr(tool_call.arguments, 'dict') else tool_call.arguments
                urls = args.get("urls", [])
                options = args.get("options")
            
            # Validate input
            if not urls:
                raise ScrapingError("URL list cannot be empty")
                
            # Perform scraping
            scrape_request = ScrapeUrlRequest(urls=urls, options=options)
            scrape_response = await self.firecrawl_client.scrape_urls(
                scrape_request.urls,
                scrape_request.options
            )
            
            # Format results for MCP
            content: list[ToolResultContent] = []
            if scrape_response.results:
                result_text = scrape_response.json(indent=2)
                content.append(TextContent(type="text", text=result_text))
            
            return ToolResult(
                contents=content,
                isError=False
            )
            
        except ScrapingError as e:
            logger.error(f"Scraping error in scrape_urls: {str(e)}")
            return ToolResult(
                contents=[TextContent(type="text", text=f"Scraping failed: {str(e)}")],
                isError=True
            )
        except Exception as e:
            logger.error(f"Unexpected error in scrape_urls: {str(e)}")
            return ToolResult(
                contents=[TextContent(type="text", text=f"Unexpected error: {str(e)}")],
                isError=True
            )
            
    async def close(self):
        """Close all client connections."""
        await self.searxng_client.close()
        await self.firecrawl_client.close()
        await self.redis_client.close()
        logger.info("MCP tools closed")
        
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()