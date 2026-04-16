"""
Search web tool for MCP Search Server.

Implements the search_web MCP tool functionality.
"""

import logging
from typing import Optional

from mcp_search.core import settings
from mcp_search.schemas import SearchRequest
from mcp_search.core.exceptions import ToolExecutionError, SearchError
from .templates import BaseTool

logger = logging.getLogger(__name__)


class SearchWebTool(BaseTool):
    """
    Tool for performing web searches using SearxNG.
    
    Implements the search_web MCP tool functionality.
    """
    
    tool_metadata = {
        "name": "search_web",
        "description": "Perform a web search using SearxNG.",
        "parameters": {
            "query": {
                "type": "string",
                "description": "The search query string"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return (default: 10, max: 50)"
            }
        }
    }

    async def execute(self, query: str, max_results: int = None) -> str:
        """
        Execute web search using SearxNG.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            JSON-formatted search results or error message
        """
        logger.info(f"Handling search_web for query: {query}")
        
        try:
            if not query:
                raise SearchError("Search query cannot be empty")
                
            if max_results is None:
                max_results = settings.default_max_results
                
            max_results = min(max_results, settings.max_search_results)
            
            search_request = SearchRequest(query=query, max_results=max_results)
            search_response = await self.searxng_client.search(
                search_request.query,
                search_request.max_results,
            )
            
            return search_response.model_dump_json(indent=2)
            
        except SearchError as e:
            logger.error(f"Search error: {str(e)}")
            return f"Search failed: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in search_web: {str(e)}")
            # Wrap unexpected errors with more specific tool execution error
            raise ToolExecutionError(
                f"Failed to execute search_web tool: {str(e)}",
                {"tool": "search_web", "error": str(e)}
            )