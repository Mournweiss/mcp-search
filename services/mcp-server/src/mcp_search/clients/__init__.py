"""
Clients package for MCP Search Server.

Contains HTTP clients for external services.
"""

from .templates import BaseClient
from .searxng import SearxNGClient
from .firecrawl import FirecrawlClient
from .redis import RedisClient

__all__ = [
    "BaseClient",
    "SearxNGClient",
    "FirecrawlClient",
    "RedisClient"
]