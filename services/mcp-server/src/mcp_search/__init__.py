"""
MCP Search Server package.
"""

__version__ = "0.1.0"
__author__ = "Maxim Selin"

from .tools import ToolRegistry
from .core import setup_logger, settings
from .core.exceptions import (
    MCPError,
    SearchError,
    ScrapingError,
    CacheError,
    ValidationError,
    RateLimitError
)


def main():
    """Lazy access to main entry point to avoid import-time side effects."""
    from .main import main as _main
    return _main


__all__ = [
    "main",
    "settings",
    "setup_logger",
    "MCPError",
    "SearchError",
    "ScrapingError",
    "CacheError",
    "ValidationError",
    "RateLimitError",
    "ToolRegistry"
]
