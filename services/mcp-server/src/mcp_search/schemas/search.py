"""
Search schemas for MCP Search Server.

Defines data models used for search operations.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """
    Model representing a search request.
    
    Defines structure of search requests received by the server.
    """
    
    query: str = Field(..., description="Search query string")
    """Search query string."""
    
    search_type: str = Field(default="general", description="Type of search (general, news, images, etc.)")
    """Type of search (general, news, images, etc.)."""
    
    max_results: int = Field(default=10, ge=1, le=50, description="Maximum number of results to return")
    """Maximum number of results to return."""
    
    categories: Optional[List[str]] = Field(default=None, description="Search categories to filter by")
    """Search categories to filter by."""


class SearchResult(BaseModel):
    """
    Model representing a single search result.
    
    Defines structure of individual search results returned by the server.
    """
    
    title: str = Field(..., description="Title of the search result")
    """Title of the search result."""
    
    url: str = Field(..., description="URL of the search result")
    """URL of the search result."""
    
    content: str = Field(..., description="Content or snippet from the search result")
    """Content or snippet from the search result."""
    
    source: str = Field(..., description="Source of the search result (searxng, firecrawl, etc.)")
    """Source of the search result (searxng, firecrawl, etc.)."""
    
    score: Optional[float] = Field(default=None, description="Relevance score of the result (optional)")
    """Relevance score of the result (optional)."""
    
    category: Optional[str] = Field(default=None, description="Category of the search result")
    """Category of the search result."""


class SearchResponse(BaseModel):
    """
    Model representing a search response.
    
    Defines structure of search responses returned by the server.
    """
    
    results: List[SearchResult] = Field(..., description="List of search results")
    """List of search results."""
    
    total_results: int = Field(..., description="Total number of results found")
    """Total number of results found."""
    
    query: str = Field(..., description="Original search query")
    """Original search query."""
    
    search_type: str = Field(default="general", description="Type of search performed")
    """Type of search performed."""