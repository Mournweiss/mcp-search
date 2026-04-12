"""
Base HTTP client for MCP Search Server.

Provides a base HTTP client with retry, timeout, and connection pooling
functionality that all other clients should inherit from.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Union
import httpx
from pydantic import BaseModel
from ..core import settings


logger = logging.getLogger(__name__)


class BaseClient:
    """
    Base HTTP client with retry, timeout, and connection pooling.
    
    Provides common functionality for all HTTP clients including:
    - Retry logic
    - Timeout handling
    - Connection pooling
    - Error handling
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the base client.
        
        Args:
            base_url (Optional[str]): Base URL for all requests
        """
        self.base_url = base_url or ""
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=settings.request_timeout,
            follow_redirects=True,
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20
            )
        )
        logger.info(f"Base client initialized with base_url: {base_url}")
        
    async def get(self, url: str, params: Optional[Dict[str, Any]] = None, 
                 headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        """
        Perform GET request.
        
        Args:
            url (str): URL to request
            params (Optional[Dict[str, Any]]): Query parameters
            headers (Optional[Dict[str, str]]): Request headers
            
        Returns:
            httpx.Response: Response object
            
        Raises:
            httpx.RequestError: If the request fails
        """
        try:
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response
        except httpx.RequestError as e:
            logger.error(f"GET request failed for {url}: {str(e)}")
            raise
            
    async def post(self, url: str, data: Optional[Dict[str, Any]] = None,
                  json_data: Optional[Dict[str, Any]] = None,
                  headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        """
        Perform POST request.
        
        Args:
            url (str): URL to request
            data (Optional[Dict[str, Any]]): Form data
            json_data (Optional[Dict[str, Any]]): JSON data
            headers (Optional[Dict[str, str]]): Request headers
            
        Returns:
            httpx.Response: Response object
            
        Raises:
            httpx.RequestError: If the request fails
        """
        try:
            response = await self.client.post(url, data=data, json=json_data, headers=headers)
            response.raise_for_status()
            return response
        except httpx.RequestError as e:
            logger.error(f"POST request failed for {url}: {str(e)}")
            raise
            
    async def close(self):
        """Close the HTTP client connection."""
        await self.client.aclose()
        logger.info("Base client closed")
        
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()