"""
Unit tests for MCP Search exception handling.
"""

import pytest
from mcp_search.core.exceptions import (
    MCPError,
    SearchError,
    ScrapingError,
    CacheError,
    ValidationError,
    RateLimitError
)


def test_mcp_error_base():
    """Test the base MCPError class."""
    error = MCPError("Test message", "TEST_ERROR", {"details": "test"})
    
    assert error.message == "Test message"
    assert error.error_code == "TEST_ERROR"
    assert error.details == {"details": "test"}
    
    # Test to_dict method
    error_dict = error.to_dict()
    assert error_dict["message"] == "Test message"
    assert error_dict["code"] == "TEST_ERROR"
    assert error_dict["details"] == {"details": "test"}


def test_search_error():
    """Test SearchError class."""
    error = SearchError("Search failed", {"query": "test"})
    
    assert error.message == "Search failed"
    assert error.error_code == "SEARCH_ERROR"
    assert error.details == {"query": "test"}
    
    # Test to_dict method
    error_dict = error.to_dict()
    assert error_dict["message"] == "Search failed"
    assert error_dict["code"] == "SEARCH_ERROR"
    assert error_dict["details"] == {"query": "test"}


def test_scraping_error():
    """Test ScrapingError class."""
    error = ScrapingError("Scraping failed", {"url": "http://example.com"})
    
    assert error.message == "Scraping failed"
    assert error.error_code == "SCRAPING_ERROR"
    assert error.details == {"url": "http://example.com"}
    
    # Test to_dict method
    error_dict = error.to_dict()
    assert error_dict["message"] == "Scraping failed"
    assert error_dict["code"] == "SCRAPING_ERROR"
    assert error_dict["details"] == {"url": "http://example.com"}


def test_cache_error():
    """Test CacheError class."""
    error = CacheError("Cache operation failed", {"key": "test_key"})
    
    assert error.message == "Cache operation failed"
    assert error.error_code == "CACHE_ERROR"
    assert error.details == {"key": "test_key"}
    
    # Test to_dict method
    error_dict = error.to_dict()
    assert error_dict["message"] == "Cache operation failed"
    assert error_dict["code"] == "CACHE_ERROR"
    assert error_dict["details"] == {"key": "test_key"}


def test_validation_error():
    """Test ValidationError class."""
    error = ValidationError("Validation failed", {"field": "invalid"})
    
    assert error.message == "Validation failed"
    assert error.error_code == "VALIDATION_ERROR"
    assert error.details == {"field": "invalid"}
    
    # Test to_dict method
    error_dict = error.to_dict()
    assert error_dict["message"] == "Validation failed"
    assert error_dict["code"] == "VALIDATION_ERROR"
    assert error_dict["details"] == {"field": "invalid"}


def test_rate_limit_error():
    """Test RateLimitError class."""
    error = RateLimitError("Rate limit exceeded", {"limit": 60})
    
    assert error.message == "Rate limit exceeded"
    assert error.error_code == "RATE_LIMIT_ERROR"
    assert error.details == {"limit": 60}
    
    # Test to_dict method
    error_dict = error.to_dict()
    assert error_dict["message"] == "Rate limit exceeded"
    assert error_dict["code"] == "RATE_LIMIT_ERROR"
    assert error_dict["details"] == {"limit": 60}


def test_exception_inheritance():
    """Test that exceptions properly inherit from MCPError."""
    search_error = SearchError("Search failed")
    scraping_error = ScrapingError("Scraping failed")
    cache_error = CacheError("Cache failed")
    validation_error = ValidationError("Validation failed")
    rate_limit_error = RateLimitError("Rate limit exceeded")
    
    # All should be instances of MCPError
    assert isinstance(search_error, MCPError)
    assert isinstance(scraping_error, MCPError)
    assert isinstance(cache_error, MCPError)
    assert isinstance(validation_error, MCPError)
    assert isinstance(rate_limit_error, MCPError)