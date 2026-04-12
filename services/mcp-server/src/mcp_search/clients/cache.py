"""
Redis cache client for MCP Search Server.

Provides a client for interacting with Redis for caching purposes.
"""

import asyncio
import logging
from typing import Optional, Any, Union
import redis.asyncio as redis
from ..core import (
    settings,
    CacheError
)


logger = logging.getLogger(__name__)


class RedisClient:
    """
    Client for interacting with Redis cache.
    
    Handles communication with the Redis service for caching operations.
    """
    
    def __init__(self):
        """Initialize the Redis client."""
        self.client: Optional[redis.Redis] = None
        logger.info("Redis client initialized")
        
    async def connect(self):
        """Establish connection to Redis."""
        try:
            self.client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=settings.connect_timeout,
                socket_timeout=settings.request_timeout
            )
            # Test the connection
            await self.client.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise CacheError(f"Redis connection failed: {str(e)}")
            
    async def get(self, key: str) -> Optional[str]:
        """
        Get value from cache.
        
        Args:
            key (str): Cache key
            
        Returns:
            Optional[str]: Cached value or None if not found
        """
        if self.client is None:
            await self.connect()
            
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"Error getting from cache key {key}: {str(e)}")
            raise CacheError(f"Cache get failed for key {key}: {str(e)}")
            
    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """
        Set value in cache.
        
        Args:
            key (str): Cache key
            value (str): Value to cache
            expire (Optional[int]): Expiration time in seconds
            
        Returns:
            bool: True if successful
        """
        if self.client is None:
            await self.connect()
            
        try:
            if expire:
                return await self.client.set(key, value, ex=expire)
            else:
                return await self.client.set(key, value)
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {str(e)}")
            raise CacheError(f"Cache set failed for key {key}: {str(e)}")
            
    async def close(self):
        """Close the Redis client connection."""
        if self.client:
            await self.client.close()
            logger.info("Redis client closed")
            
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()