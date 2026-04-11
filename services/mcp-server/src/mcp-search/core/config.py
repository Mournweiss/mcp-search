"""
Configuration for MCP Search Server.

Defines all configuration parameters for the MCP Search server.
"""

import os
from typing import Optional, Union
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings using Pydantic Settings.
    
    Defines all configuration parameters for the MCP Search server.
    """
    
    # Logging configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # Service endpoints
    searxng_url: str = Field(default="http://searxng:8080", env="SEARXNG_URL")
    firecrawl_url: str = Field(default="http://firecrawl:3000", env="FIRECRAWL_URL")
    mcp_port: int = Field(default=8000, env="MCP_PORT")
    
    # Rate limiting configuration
    enable_rate_limiting: bool = Field(default=True, env="ENABLE_RATE_LIMITING")
    rate_limit_requests: int = Field(default=60, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # Caching configuration
    redis_url: str = Field(default="redis://redis:6379", env="REDIS_URL")
    redis_cache_ttl: int = Field(default=3600, env="REDIS_CACHE_TTL")  # 1 hour by default
    
    # Scraping configuration
    max_concurrent_requests: int = Field(default=10, env="MAX_CONCURRENT_REQUESTS")
    max_queue_size: int = Field(default=100, env="MAX_QUEUE_SIZE")
    
    # Timeout configuration
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    connect_timeout: int = Field(default=10, env="CONNECT_TIMEOUT")
    
    # Search configuration
    default_max_results: int = Field(default=10, env="DEFAULT_MAX_RESULTS")
    max_search_results: int = Field(default=50, env="MAX_SEARCH_RESULTS")
    
    # API Keys and Security
    mcp_api_key: Optional[str] = Field(default=None, env="MCP_API_KEY")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False


settings = Settings()