"""
Scraping schemas for MCP Search Server.

Defines data models used for scraping operations.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ScrapeUrlRequest(BaseModel):
    """
    Model representing a URL scraping request.
    
    Defines structure of scraping requests containing URLs to process.
    """
    
    urls: List[str] = Field(..., description="List of URLs to scrape")
    """List of URLs to scrape."""
    
    options: Optional[Dict[str, Any]] = Field(default=None, description="Additional options for scraping (optional)")
    """Additional options for scraping (optional)."""


class ScrapingResult(BaseModel):
    """
    Model representing a single scraping result.
    
    Defines structure of individual scraping results returned by the server.
    """
    
    url: str = Field(..., description="URL that was scraped")
    """URL that was scraped."""
    
    title: Optional[str] = Field(default=None, description="Title of the scraped page")
    """Title of the scraped page."""
    
    content: str = Field(..., description="Main content of the scraped page")
    """Main content of the scraped page."""
    
    raw_content: Optional[str] = Field(default=None, description="Raw content from the scraped page (optional)")
    """Raw content from the scraped page (optional)."""
    
    links: List[str] = Field(default=[], description="List of links found on the page")
    """List of links found on the page."""
    
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata about the scraped page (optional)")
    """Additional metadata about the scraped page (optional)."""
    
    source: str = Field(default="firecrawl", description="Source of the scraping result")
    """Source of the scraping result."""


class ScrapeResponse(BaseModel):
    """
    Model representing a scraping response.
    
    Defines structure of scraping responses returned by the server.
    """
    
    results: List[ScrapingResult] = Field(..., description="List of scraping results")
    """List of scraping results."""
    
    total_scraped: int = Field(..., description="Total number of URLs successfully scraped")
    """Total number of URLs successfully scraped."""
    
    total_failed: int = Field(default=0, description="Number of URLs that failed to scrape")
    """Number of URLs that failed to scrape."""
    
    failed_urls: List[str] = Field(default=[], description="List of URLs that failed to scrape")
    """List of URLs that failed to scrape."""