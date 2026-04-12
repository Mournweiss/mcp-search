"""
Unit tests for MCP Search scrape schemas.
"""

import pytest
from mcp_search.schemas.scrape import (
    ScrapeUrlRequest,
    ScrapingResult,
    ScrapeResponse
)


def test_scrape_url_request_validation():
    """Test ScrapeUrlRequest validation."""
    # Test valid request with URLs
    request = ScrapeUrlRequest(
        urls=["http://example.com/test1", "http://example.com/test2"]
    )
    
    assert request.urls == ["http://example.com/test1", "http://example.com/test2"]
    assert request.options is None
    
    # Test request with options
    request_with_options = ScrapeUrlRequest(
        urls=["http://example.com/test"],
        options={"includeHtml": True, "includeLinks": False}
    )
    
    assert request_with_options.urls == ["http://example.com/test"]
    assert request_with_options.options == {"includeHtml": True, "includeLinks": False}


def test_scrape_url_request_empty_urls():
    """Test ScrapeUrlRequest with empty URLs list."""
    # Test with empty URLs list (should raise validation error)
    with pytest.raises(ValueError):
        ScrapeUrlRequest(urls=[])


def test_scraping_result():
    """Test ScrapingResult data structure."""
    result = ScrapingResult(
        url="http://example.com/test",
        title="Test Title",
        content="Test content for the scraped page",
        raw_content="<html><body>Raw content</body></html>",
        links=["http://example.com/link1", "http://example.com/link2"],
        metadata={"author": "Test Author", "date": "2023-01-01"},
        source="firecrawl"
    )
    
    assert result.url == "http://example.com/test"
    assert result.title == "Test Title"
    assert result.content == "Test content for the scraped page"
    assert result.raw_content == "<html><body>Raw content</body></html>"
    assert result.links == ["http://example.com/link1", "http://example.com/link2"]
    assert result.metadata == {"author": "Test Author", "date": "2023-01-01"}
    assert result.source == "firecrawl"


def test_scraping_result_optional_fields():
    """Test ScrapingResult with optional fields."""
    # Test with None values for optional fields
    result = ScrapingResult(
        url="http://example.com/test",
        title=None,
        content="Test content",
        raw_content=None,
        links=[],
        metadata=None,
        source="firecrawl"
    )
    
    assert result.title is None
    assert result.raw_content is None
    assert result.links == []
    assert result.metadata is None


def test_scraping_result_default_values():
    """Test ScrapingResult default values."""
    result = ScrapingResult(
        url="http://example.com/test",
        title="Test Title",
        content="Test content"
    )
    
    # Test defaults
    assert result.raw_content is None
    assert result.links == []
    assert result.metadata is None
    assert result.source == "firecrawl"


def test_scrape_response():
    """Test ScrapeResponse data structure."""
    # Test with empty results
    response = ScrapeResponse(
        results=[],
        total_scraped=0,
        total_failed=0,
        failed_urls=[]
    )
    
    assert response.results == []
    assert response.total_scraped == 0
    assert response.total_failed == 0
    assert response.failed_urls == []


def test_scrape_response_with_results():
    """Test ScrapeResponse with actual results."""
    # Create a sample scraping result
    from mcp_search.schemas.scrape import ScrapingResult
    
    result = ScrapingResult(
        url="http://example.com/test",
        title="Test Title",
        content="Test content"
    )
    
    response = ScrapeResponse(
        results=[result],
        total_scraped=1,
        total_failed=0,
        failed_urls=[]
    )
    
    assert len(response.results) == 1
    assert response.total_scraped == 1
    assert response.total_failed == 0
    assert response.failed_urls == []
    
    # Verify the result data
    assert response.results[0].url == "http://example.com/test"
    assert response.results[0].title == "Test Title"


def test_scrape_response_with_failures():
    """Test ScrapeResponse with failed URLs."""
    response = ScrapeResponse(
        results=[],
        total_scraped=5,
        total_failed=2,
        failed_urls=["http://example.com/fail1", "http://example.com/fail2"]
    )
    
    assert response.total_scraped == 5
    assert response.total_failed == 2
    assert response.failed_urls == ["http://example.com/fail1", "http://example.com/fail2"]