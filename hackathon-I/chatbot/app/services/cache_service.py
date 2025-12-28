from typing import Optional, Dict, Any
import hashlib
import json
import asyncio
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CacheEntry:
    """
    Runtime model for tracking cached responses with TTL.
    """
    def __init__(self, response: Dict[str, Any], ttl_seconds: int = 300):  # 5 minutes default
        self.response = response
        self.created_at = datetime.utcnow()
        self.ttl_seconds = ttl_seconds

    @property
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return datetime.utcnow() > (self.created_at + timedelta(seconds=self.ttl_seconds))


class ResponseCache:
    """
    In-memory response cache for repeated queries.
    """
    def __init__(self, default_ttl_seconds: int = 300):  # 5 minutes default
        self.default_ttl = default_ttl_seconds
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()  # Thread-safe operations

    def _generate_key(self, message: str, context_selection: Optional[str] = None) -> str:
        """
        Generate a cache key based on the query parameters.

        Args:
            message: The user's question
            context_selection: Optional selected text context

        Returns:
            Hashed key for cache lookup
        """
        # Create a consistent key from the query parameters
        cache_input = {
            'message': message.strip().lower(),
            'context_selection': context_selection.strip().lower() if context_selection else None
        }

        # Create a hash of the cache input to use as key
        cache_str = json.dumps(cache_input, sort_keys=True, default=str)
        return hashlib.sha256(cache_str.encode()).hexdigest()

    async def get(self, message: str, context_selection: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached response if available and not expired.

        Args:
            message: The user's question
            context_selection: Optional selected text context

        Returns:
            Cached response or None if not found/expired
        """
        key = self._generate_key(message, context_selection)

        async with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if not entry.is_expired:
                    logger.info(f"Cache HIT for key: {key[:8]}...")
                    return entry.response
                else:
                    # Remove expired entry
                    del self._cache[key]
                    logger.info(f"Cache EXPIRED for key: {key[:8]}...")

            logger.info(f"Cache MISS for key: {key[:8]}...")
            return None

    async def set(self, message: str, context_selection: Optional[str], response: Dict[str, Any], ttl_seconds: Optional[int] = None) -> None:
        """
        Store response in cache.

        Args:
            message: The user's question
            context_selection: Optional selected text context
            response: The response to cache
            ttl_seconds: Time-to-live in seconds (uses default if not provided)
        """
        key = self._generate_key(message, context_selection)
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl

        async with self._lock:
            self._cache[key] = CacheEntry(response, ttl)
            logger.info(f"Cache SET for key: {key[:8]}... (TTL: {ttl}s)")

    async def clear_expired(self) -> int:
        """
        Remove all expired entries from cache.

        Returns:
            Number of entries removed
        """
        async with self._lock:
            expired_keys = []
            for key, entry in self._cache.items():
                if entry.is_expired:
                    expired_keys.append(key)

            for key in expired_keys:
                del self._cache[key]

            logger.info(f"Cleared {len(expired_keys)} expired cache entries")
            return len(expired_keys)

    async def clear_all(self) -> None:
        """Clear all entries from cache."""
        async with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Cleared all {count} cache entries")


# Global instance
response_cache = ResponseCache()