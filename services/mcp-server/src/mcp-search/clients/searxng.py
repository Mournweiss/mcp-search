"""
SearxNG client for MCP Search Server.

Provides a client for interacting with the SearxNG search engine API,
handling search requests and parsing responses.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
import httpx

from ..schemas import SearchResult, SearchResponse
from .base import BaseClient
from ..core import (
    settings,
    SearchError
)


logger = logging.getLogger(__name__)


class SearxNGClient(BaseClient):
    """
    Client for interacting with the SearxNG search engine API.
    
    Handles communication with the SearxNG service for performing searches.
    """
    
    def __init__(self):
        """Initialize the SearxNG client with appropriate timeouts and settings."""
        super().__init__(base_url=settings.searxng_url)
        logger.info("SearxNG client initialized")
        
    async def search(self, query: str, max_results: int = 10) -> SearchResponse:
        """
        Perform a search using SearxNG API.
        
        Args:
            query (str): Search query string
            max_results (int): Maximum number of results to return
            
        Returns:
            SearchResponse: Structured search results
            
        Raises:
            SearchError: If the search operation fails
        """
        try:
            logger.info(f"Performing SearxNG search for query: {query}")
            
            # SearxNG API endpoint
            response = await self.get(
                "/search",
                params={
                    "q": query,
                    "format": "json",
                    "limit": max_results
                }
            )
            
            if response.status_code == 200:
                results_data = response.json()
                search_results = []
                
                for result in results_data.get("results", []):
                    search_results.append(
                        SearchResult(
                            title=result.get("title", ""),
                            url=result.get("url", ""),
                            content=result.get("content", ""),
                            source="searxng",
                            score=result.get("score"),
                            category=result.get("category")
                        )
                    )
                
                logger.info(f"Found {len(search_results)} results from SearxNG")
                return SearchResponse(
                    results=search_results,
                    total_results=len(search_results),
                    query=query,
                    search_type="general"
                )
            else:
                error_msg = f"SearxNG search failed with status {response.status_code}"
                logger.error(error_msg)
                raise SearchError(error_msg)
                
        except httpx.RequestError as e:
            error_msg = f"Network error during SearxNG search: {str(e)}"
            logger.error(error_msg)
            raise SearchError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during SearxNG search: {str(e)}"
            logger.error(error_msg)
            raise SearchError(error_msg)
            
    async def close(self):
        """Close the HTTP client connection."""
        await super().close()