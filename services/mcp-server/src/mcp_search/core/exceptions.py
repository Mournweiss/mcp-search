"""
Custom exceptions for MCP Search Server.

Defines custom exceptions that are compatible with MCP protocol
and provide structured error handling.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel


class MCPError(Exception):
    """
    Base exception class for MCP Search Server errors.
    """
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize MCPError.
        
        Args:
            message (str): Error message
            error_code (Optional[str]): Error code for MCP compatibility
            details (Optional[Dict[str, Any]]): Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary format for MCP responses.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the error
        """
        result = {
            "message": self.message
        }
        if self.error_code:
            result["code"] = self.error_code
        if self.details:
            result["details"] = self.details
        return result


class SearchError(MCPError):
    """
    Exception raised when search operations fail.
    
    Used when SearxNG search operations encounter problems.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize SearchError.
        
        Args:
            message (str): Error message
            details (Optional[Dict[str, Any]]): Additional error details
        """
        super().__init__(message, "SEARCH_ERROR", details)


class ScrapingError(MCPError):
    """
    Exception raised when scraping operations fail.
    
    Used when Firecrawl scraping operations encounter problems.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize ScrapingError.
        
        Args:
            message (str): Error message
            details (Optional[Dict[str, Any]]): Additional error details
        """
        super().__init__(message, "SCRAPING_ERROR", details)


class CacheError(MCPError):
    """
    Exception raised when cache operations fail.
    
    Used when Redis cache operations encounter problems.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize CacheError.
        
        Args:
            message (str): Error message
            details (Optional[Dict[str, Any]]): Additional error details
        """
        super().__init__(message, "CACHE_ERROR", details)


class ValidationError(MCPError):
    """
    Exception raised when input validation fails.
    
    Used when request parameters don't meet validation criteria.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize ValidationError.
        
        Args:
            message (str): Error message
            details (Optional[Dict[str, Any]]): Additional error details
        """
        super().__init__(message, "VALIDATION_ERROR", details)


class RateLimitError(MCPError):
    """
    Exception raised when rate limiting is exceeded.
    
    Used when request rate limits are exceeded.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize RateLimitError.
        
        Args:
            message (str): Error message
            details (Optional[Dict[str, Any]]): Additional error details
        """
        super().__init__(message, "RATE_LIMIT_ERROR", details)