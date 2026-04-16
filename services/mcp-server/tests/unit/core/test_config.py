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


def test_settings_edge_cases():
    """Test settings with edge case values."""
    # Test with empty string values
    with patch.dict('os.environ', {
        'LOG_LEVEL': '',
        'SEARXNG_URL': '',
        'MCP_PORT': '0'
    }):
        settings = Settings()
        
        assert settings.log_level == ""
        assert settings.searxng_url == ""
        assert settings.mcp_port == 0


def test_settings_boolean_conversion():
    """Test that boolean values are properly converted."""
    with patch.dict('os.environ', {
        'ENABLE_RATE_LIMITING': 'false',
        'MCP_API_KEY': 'test-key'
    }):
        settings = Settings()
        
        assert settings.enable_rate_limiting is False
        assert settings.mcp_api_key == "test-key"


def test_settings_integer_conversion():
    """Test that integer values are properly converted."""
    with patch.dict('os.environ', {
        'MCP_PORT': '8080',
        'RATE_LIMIT_REQUESTS': '100',
        'REQUEST_TIMEOUT': '60'
    }):
        settings = Settings()
        
        assert settings.mcp_port == 8080
        assert settings.rate_limit_requests == 100
        assert settings.request_timeout == 60


def test_settings_complex_env_combinations():
    """Test complex combinations of environment variables."""
    with patch.dict('os.environ', {
        'LOG_LEVEL': 'DEBUG',
        'SEARXNG_URL': 'http://custom-searxng:8080',
        'FIRECRAWL_URL': 'http://custom-firecrawl:3000',
        'MCP_PORT': '9000',
        'ENABLE_RATE_LIMITING': 'false',
        'RATE_LIMIT_REQUESTS': '50',
        'REDIS_CACHE_TTL': '7200'
    }):
        settings = Settings()
        
        assert settings.log_level == "DEBUG"
        assert settings.searxng_url == "http://custom-searxng:8080"
        assert settings.firecrawl_url == "http://custom-firecrawl:3000"
        assert settings.mcp_port == 9000
        assert settings.enable_rate_limiting is False
        assert settings.rate_limit_requests == 50
        assert settings.redis_cache_ttl == 7200


def test_settings_default_inheritance():
    """Test that default values are properly inherited."""
    settings = Settings()
    
    # Test that all expected fields exist with their defaults
    expected_defaults = {
        'log_level': 'INFO',
        'log_format': 'json',
        'searxng_url': 'http://searxng:8080',
        'firecrawl_url': 'http://firecrawl:3000',
        'mcp_port': 8000,
        'enable_rate_limiting': True,
        'rate_limit_requests': 60,
        'rate_limit_window': 60,
        'redis_url': 'redis://redis:6379',
        'redis_cache_ttl': 3600,
        'max_concurrent_requests': 10,
        'max_queue_size': 100,
        'request_timeout': 30,
        'connect_timeout': 10,
        'default_max_results': 10,
        'max_search_results': 50,
        'mcp_api_key': None
    }
    
    for field, expected_value in expected_defaults.items():
        assert getattr(settings, field) == expected_value


def test_settings_multiple_env_var_types():
    """Test that different types of environment variables work correctly."""
    with patch.dict('os.environ', {
        'LOG_LEVEL': 'WARNING',
        'MCP_PORT': '443',
        'REQUEST_TIMEOUT': '15',
        'CONNECT_TIMEOUT': '5',
        'DEFAULT_MAX_RESULTS': '20',
        'MAX_SEARCH_RESULTS': '100'
    }):
        settings = Settings()
        
        assert settings.log_level == "WARNING"
        assert settings.mcp_port == 443
        assert settings.request_timeout == 15
        assert settings.connect_timeout == 5
        assert settings.default_max_results == 20
        assert settings.max_search_results == 100