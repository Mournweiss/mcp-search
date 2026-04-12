"""
Unit tests for MCP Search configuration module.
"""

import pytest
from unittest.mock import patch
from mcp_search.core.config import Settings


def test_settings_defaults():
    """Test that settings have correct default values."""
    settings = Settings()
    
    # Test logging configuration
    assert settings.log_level == "INFO"
    assert settings.log_format == "json"
    
    # Test service endpoints
    assert settings.searxng_url == "http://searxng:8080"
    assert settings.firecrawl_url == "http://firecrawl:3000"
    assert settings.mcp_port == 8000
    
    # Test rate limiting configuration
    assert settings.enable_rate_limiting is True
    assert settings.rate_limit_requests == 60
    assert settings.rate_limit_window == 60
    
    # Test caching configuration
    assert settings.redis_url == "redis://redis:6379"
    assert settings.redis_cache_ttl == 3600
    
    # Test scraping configuration
    assert settings.max_concurrent_requests == 10
    assert settings.max_queue_size == 100
    
    # Test timeout configuration
    assert settings.request_timeout == 30
    assert settings.connect_timeout == 10
    
    # Test search configuration
    assert settings.default_max_results == 10
    assert settings.max_search_results == 50
    
    # Test API Keys and Security
    assert settings.mcp_api_key is None


def test_settings_from_env_vars():
    """Test that settings can be overridden by environment variables."""
    with patch.dict('os.environ', {
        'LOG_LEVEL': 'DEBUG',
        'SEARXNG_URL': 'http://custom-searxng:8080',
        'MCP_PORT': '9000'
    }):
        settings = Settings()
        
        assert settings.log_level == "DEBUG"
        assert settings.searxng_url == "http://custom-searxng:8080"
        assert settings.mcp_port == 9000


def test_settings_validation():
    """Test that settings validation works correctly."""
    # Test with valid values
    settings = Settings()
    assert hasattr(settings, 'log_level')
    assert hasattr(settings, 'searxng_url')
    
    # Test that we can access all defined fields
    fields = [
        'log_level', 'log_format', 'searxng_url', 'firecrawl_url', 'mcp_port',
        'enable_rate_limiting', 'rate_limit_requests', 'rate_limit_window',
        'redis_url', 'redis_cache_ttl', 'max_concurrent_requests', 
        'max_queue_size', 'request_timeout', 'connect_timeout',
        'default_max_results', 'max_search_results', 'mcp_api_key'
    ]
    
    for field in fields:
        assert hasattr(settings, field)