"""
Firecrawl client for MCP Search Server.

Provides a client for interacting with the Firecrawl scraping API,
handling URL scraping requests and parsing responses.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
import httpx

from mcp_search.schemas import ScrapingResult, ScrapeResponse
from mcp_search.core import settings
from mcp_search.core.exceptions import ScrapingError
from .templates import BaseClient


logger = logging.getLogger(__name__)


class FirecrawlClient(BaseClient):
    """
    Client for interacting with the Firecrawl scraping API.
    
    Handles communication with the Firecrawl service for scraping URLs.
    """
    
    def __init__(self):
        """Initialize the Firecrawl client with appropriate timeouts and settings."""
        super().__init__(base_url=settings.firecrawl_url)
        logger.info("Firecrawl client initialized")
        
    async def scrape_urls(self, urls: List[str], options: Optional[Dict[str, Any]] = None) -> ScrapeResponse:
        """
        Scrape multiple URLs using Firecrawl API.
        
        Args:
            urls (List[str]): List of URLs to scrape
            options (Optional[Dict[str, Any]]): Additional scraping options
            
        Returns:
            ScrapeResponse: Structured scraping results
            
        Raises:
            ScrapingError: If the scraping operation fails
        """
        try:
            logger.info(f"Scraping {len(urls)} URLs with Firecrawl")
            
            # Prepare scraping tasks
            tasks = []
            for url in urls:
                task = self._scrape_single_url(url, options)
                tasks.append(task)
            
            # Execute scraping tasks concurrently with limit
            semaphore = asyncio.Semaphore(settings.max_concurrent_requests)
            
            async def limited_scrape(url, opts):
                async with semaphore:
                    return await self._scrape_single_url(url, opts)
            
            # Run tasks with concurrency limit
            results = await asyncio.gather(
                *[limited_scrape(url, options) for url in urls],
                return_exceptions=True
            )
            
            # Process results
            scraping_results = []
            failed_urls = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to scrape URL {urls[i]}: {str(result)}")
                    failed_urls.append(urls[i])
                else:
                    scraping_results.append(result)
            
            logger.info(f"Successfully scraped {len(scraping_results)} URLs, {len(failed_urls)} failed")
            
            return ScrapeResponse(
                results=scraping_results,
                total_scraped=len(scraping_results),
                total_failed=len(failed_urls),
                failed_urls=failed_urls
            )
            
        except Exception as e:
            error_msg = f"Unexpected error during Firecrawl scraping: {str(e)}"
            logger.error(error_msg)
            raise ScrapingError(error_msg)
            
    async def _scrape_single_url(self, url: str, options: Optional[Dict[str, Any]] = None) -> ScrapingResult:
        """
        Scrape a single URL using Firecrawl API.
        
        Args:
            url (str): URL to scrape
            options (Optional[Dict[str, Any]]): Additional scraping options
            
        Returns:
            ScrapingResult: Structured scraping result for the URL
            
        Raises:
            ScrapingError: If the scraping operation fails for this specific URL
        """
        try:
            logger.debug(f"Scraping single URL: {url}")
            
            # Firecrawl API endpoint
            payload = {
                "url": url,
                "limit": 1000  # Default limit for content length
            }
            
            if options:
                payload.update(options)
                
            response = await self.post(
                "/scrape",
                json=payload
            )
            
            if response.status_code == 200:
                result_data = response.json()
                
                return ScrapingResult(
                    url=url,
                    title=result_data.get("title", ""),
                    content=result_data.get("content", ""),
                    raw_content=result_data.get("rawContent"),
                    links=result_data.get("links", []),
                    metadata=result_data.get("metadata"),
                    source="firecrawl"
                )
            else:
                error_msg = f"Firecrawl scraping failed for {url} with status {response.status_code}"
                logger.error(error_msg)
                raise ScrapingError(error_msg)
                
        except httpx.RequestError as e:
            error_msg = f"Network error while scraping {url}: {str(e)}"
            logger.error(error_msg)
            raise ScrapingError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error while scraping {url}: {str(e)}"
            logger.error(error_msg)
            raise ScrapingError(error_msg)
            
    async def close(self):
        """Close the HTTP client connection."""
        await super().close()