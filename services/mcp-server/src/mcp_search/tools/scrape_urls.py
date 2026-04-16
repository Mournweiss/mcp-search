"""
Scrape URLs tool for MCP Search Server.

Implements the scrape_urls MCP tool functionality.
"""

import logging
from typing import Optional, List, Dict, Any

from mcp_search.core import settings
from mcp_search.schemas import ScrapeUrlRequest
from mcp_search.core.exceptions import ToolExecutionError, ScrapingError
from .templates import BaseTool

logger = logging.getLogger(__name__)


class ScrapeUrlsTool(BaseTool):
    """
    Tool for scraping URLs using Firecrawl.
    
    Implements the scrape_urls MCP tool functionality.
    """
    
    tool_metadata = {
        "name": "scrape_urls",
        "description": "Scrape one or more URLs using Firecrawl.",
        "parameters": {
            "urls": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of URLs to scrape"
            },
            "options": {
                "type": "object",
                "description": "Optional additional scraping parameters"
            }
        }
    }

    async def execute(self, urls: List[str], options: Optional[Dict[str, Any]] = None) -> str:
        """
        Execute URL scraping using Firecrawl.
        
        Args:
            urls: List of URLs to scrape
            options: Optional scraping parameters
            
        Returns:
            JSON-formatted scraping results or error message
        """
        logger.info(f"Handling scrape_urls for {len(urls)} URLs")
        
        try:
            if not urls:
                raise ScrapingError("URL list cannot be empty")
                
            scrape_request = ScrapeUrlRequest(urls=urls, options=options)
            scrape_response = await self.firecrawl_client.scrape_urls(
                scrape_request.urls,
                scrape_request.options,
            )
            
            return scrape_response.model_dump_json(indent=2)
            
        except ScrapingError as e:
            logger.error(f"Scraping error: {str(e)}")
            return f"Scraping failed: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in scrape_urls: {str(e)}")
            raise ToolExecutionError(
                f"Failed to execute scrape_urls tool: {str(e)}",
                {"tool": "scrape_urls", "error": str(e)}
            )