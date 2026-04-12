"""
MCP Search Server package.
"""

__version__ = "0.1.0"
__author__ = "Maxim Selin"

from .main import main, MCPSever
from .core import (
    setup_logger,
    settings,
    MCPError,
    SearchError,
    ScrapingError,
    CacheError,
    ValidationError,
    RateLimitError
)
from .server.tools import MCPTools

__all__ = [
    "main",
    "MCPSever",
    "settings",
    "setup_logger",
    "MCPError",
    "SearchError",
    "ScrapingError",
    "CacheError",
    "ValidationError",
    "RateLimitError",
    "MCPTools"
]