"""
Core modules for MCP Search Server.

Contains core functionality including configuration,
logging, and exception handling.
"""

from .config import settings
from .logging import setup_logger
from .exceptions import (
    MCPError,
    SearchError,
    ScrapingError,
    CacheError,
    ValidationError,
    RateLimitError
)

__all__ = [
    "settings",
    "setup_logger",
    "MCPError",
    "SearchError",
    "ScrapingError",
    "CacheError",
    "ValidationError",
    "RateLimitError"
]