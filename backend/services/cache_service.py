"""
Cache service for Redis-based caching.
"""
import redis
import json
from typing import Optional, Any
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """
    Simple Redis cache wrapper for storing settings and other data.

    Uses Redis for fast, distributed caching across workers.
    """

    def __init__(self):
        """Initialize Redis connection."""
        try:
            # Parse Redis URL from settings
            self.redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True  # Auto-decode bytes to strings
            )
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis cache connected")
        except Exception as e:
            logger.warning(f"⚠️ Redis unavailable: {e}. Cache disabled.")
            self.redis_client = None

    def get(self, key: str) -> Optional[str]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/cache unavailable
        """
        if not self.redis_client:
            return None

        try:
            return self.redis_client.get(key)
        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            return None

    def set(self, key: str, value: str, ttl: int = 300) -> bool:
        """
        Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 300 = 5 minutes)

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            self.redis_client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.

        Args:
            pattern: Redis pattern (e.g., "settings:*")

        Returns:
            Number of keys deleted
        """
        if not self.redis_client:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for '{pattern}': {e}")
            return 0


# Global cache instance
_cache_service = None


def get_cache_service() -> CacheService:
    """
    Get or create global cache service instance.

    Returns:
        CacheService instance
    """
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
