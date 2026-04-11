"""
Schemas package for MCP Search Server.

Contains Pydantic models for input/output validation.
"""

from .search import SearchRequest, SearchResult, SearchResponse
from .scrape import ScrapeUrlRequest, ScrapingResult, ScrapeResponse

__all__ = [
    "SearchRequest",
    "SearchResult",
    "SearchResponse",
    "ScrapeUrlRequest",
    "ScrapingResult",
    "ScrapeResponse"
]