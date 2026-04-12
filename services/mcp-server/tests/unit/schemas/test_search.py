"""
Unit tests for MCP Search search schemas.
"""

import pytest
from mcp_search.schemas.search import (
    SearchRequest,
    SearchResult,
    SearchResponse
)


def test_search_request_validation():
    """Test SearchRequest validation."""
    # Test valid request
    request = SearchRequest(
        query="test query",
        search_type="general",
        max_results=10
    )
    
    assert request.query == "test query"
    assert request.search_type == "general"
    assert request.max_results == 10
    
    # Test with categories
    request_with_categories = SearchRequest(
        query="test query",
        search_type="news",
        max_results=5,
        categories=["technology", "science"]
    )
    
    assert request_with_categories.query == "test query"
    assert request_with_categories.search_type == "news"
    assert request_with_categories.max_results == 5
    assert request_with_categories.categories == ["technology", "science"]
    
    # Test default values
    request_defaults = SearchRequest(query="test")
    assert request_defaults.search_type == "general"
    assert request_defaults.max_results == 10
    assert request_defaults.categories is None


def test_search_request_validation_errors():
    """Test SearchRequest validation error cases."""
    # Test empty query
    with pytest.raises(ValueError):
        SearchRequest(query="")
    
    # Test max_results out of range
    with pytest.raises(ValueError):
        SearchRequest(query="test", max_results=0)
    
    with pytest.raises(ValueError):
        SearchRequest(query="test", max_results=100)


def test_search_result():
    """Test SearchResult data structure."""
    result = SearchResult(
        title="Test Title",
        url="http://example.com/test",
        content="Test content for the search result",
        source="searxng",
        score=0.8,
        category="general"
    )
    
    assert result.title == "Test Title"
    assert result.url == "http://example.com/test"
    assert result.content == "Test content for the search result"
    assert result.source == "searxng"
    assert result.score == 0.8
    assert result.category == "general"


def test_search_result_optional_fields():
    """Test SearchResult with optional fields."""
    # Test with None values for optional fields
    result = SearchResult(
        title="Test Title",
        url="http://example.com/test",
        content="Test content",
        source="searxng"
        # score and category are None by default
    )
    
    assert result.score is None
    assert result.category is None


def test_search_response():
    """Test SearchResponse data structure."""
    # Test with empty results
    response = SearchResponse(
        results=[],
        total_results=0,
        query="test query",
        search_type="general"
    )
    
    assert response.results == []
    assert response.total_results == 0
    assert response.query == "test query"
    assert response.search_type == "general"


def test_search_response_with_results():
    """Test SearchResponse with actual results."""
    # Create a sample result
    from mcp_search.schemas.search import SearchResult
    
    result = SearchResult(
        title="Test Title",
        url="http://example.com/test",
        content="Test content",
        source="searxng"
    )
    
    response = SearchResponse(
        results=[result],
        total_results=1,
        query="test query",
        search_type="news"
    )
    
    assert len(response.results) == 1
    assert response.total_results == 1
    assert response.query == "test query"
    assert response.search_type == "news"
    
    # Verify the result data
    assert response.results[0].title == "Test Title"