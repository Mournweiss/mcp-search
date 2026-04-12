"""
Helper functions for MCP Search tests.
"""

import json
from typing import Dict, Any


def create_mock_search_result(**kwargs) -> Dict[str, Any]:
    """
    Create a mock search result dictionary with default values.
    
    Args:
        **kwargs: Override default values
        
    Returns:
        Dict[str, Any]: Mock search result data
    """
    defaults = {
        "title": "Test Title",
        "url": "http://example.com/test",
        "content": "Test content for the search result",
        "source": "searxng",
        "score": 0.8,
        "category": "general"
    }
    
    defaults.update(kwargs)
    return defaults


def create_mock_search_response(results=None, **kwargs) -> Dict[str, Any]:
    """
    Create a mock search response dictionary with default values.
    
    Args:
        results: List of search results
        **kwargs: Override default values
        
    Returns:
        Dict[str, Any]: Mock search response data
    """
    if results is None:
        results = [create_mock_search_result()]
    
    defaults = {
        "results": results,
        "total_results": len(results),
        "query": "test query",
        "search_type": "general"
    }
    
    defaults.update(kwargs)
    return defaults


def create_mock_scraping_result(**kwargs) -> Dict[str, Any]:
    """
    Create a mock scraping result dictionary with default values.
    
    Args:
        **kwargs: Override default values
        
    Returns:
        Dict[str, Any]: Mock scraping result data
    """
    defaults = {
        "url": "http://example.com/test",
        "title": "Test Title",
        "content": "Test content for the scraped page",
        "raw_content": "<html><body>Raw content</body></html>",
        "links": ["http://example.com/link1", "http://example.com/link2"],
        "metadata": {"author": "Test Author"},
        "source": "firecrawl"
    }
    
    defaults.update(kwargs)
    return defaults


def create_mock_scrape_response(results=None, **kwargs) -> Dict[str, Any]:
    """
    Create a mock scrape response dictionary with default values.
    
    Args:
        results: List of scraping results
        **kwargs: Override default values
        
    Returns:
        Dict[str, Any]: Mock scrape response data
    """
    if results is None:
        results = [create_mock_scraping_result()]
    
    defaults = {
        "results": results,
        "total_scraped": len(results),
        "total_failed": 0,
        "failed_urls": []
    }
    
    defaults.update(kwargs)
    return defaults


def json_serialize(obj):
    """
    Helper function to serialize objects for testing.
    
    Args:
        obj: Object to serialize
        
    Returns:
        str: JSON serialized string
    """
    return json.dumps(obj, indent=2)