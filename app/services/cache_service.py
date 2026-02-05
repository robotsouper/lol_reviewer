"""Simple in-memory cache service with TTL support."""

import time
import logging
from threading import Lock

logger = logging.getLogger(__name__)


class CacheService:
    """
    Simple in-memory cache with time-to-live (TTL) expiration.

    This cache stores data temporarily to reduce redundant API calls
    and respect rate limits.
    """

    def __init__(self, default_ttl=300):
        """
        Initialize cache service.

        Args:
            default_ttl: Default time-to-live in seconds (default: 5 minutes)
        """
        self.default_ttl = default_ttl
        self.cache = {}
        self.lock = Lock()

    def get(self, key):
        """
        Retrieve value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        with self.lock:
            if key not in self.cache:
                logger.debug(f"Cache miss: {key}")
                return None

            entry = self.cache[key]
            timestamp = entry['timestamp']
            ttl = entry.get('ttl', self.default_ttl)

            # Check if expired
            if self._is_expired(timestamp, ttl):
                logger.debug(f"Cache expired: {key}")
                del self.cache[key]
                return None

            logger.debug(f"Cache hit: {key}")
            return entry['value']

    def set(self, key, value, ttl=None):
        """
        Store value in cache with timestamp.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (optional, uses default if not specified)
        """
        with self.lock:
            self.cache[key] = {
                'value': value,
                'timestamp': time.time(),
                'ttl': ttl if ttl is not None else self.default_ttl
            }
            logger.debug(f"Cache set: {key} (TTL: {ttl or self.default_ttl}s)")

    def delete(self, key):
        """
        Delete a specific key from cache.

        Args:
            key: Cache key to delete
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Cache deleted: {key}")

    def clear(self):
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            logger.info("Cache cleared")

    def clear_expired(self):
        """
        Remove all expired entries from cache.

        This can be called periodically to free up memory.
        """
        with self.lock:
            current_time = time.time()
            expired_keys = []

            for key, entry in self.cache.items():
                timestamp = entry['timestamp']
                ttl = entry.get('ttl', self.default_ttl)
                if self._is_expired(timestamp, ttl):
                    expired_keys.append(key)

            for key in expired_keys:
                del self.cache[key]

            if expired_keys:
                logger.info(f"Cleared {len(expired_keys)} expired cache entries")

    def _is_expired(self, timestamp, ttl):
        """
        Check if a cached entry has expired.

        Args:
            timestamp: Entry creation timestamp
            ttl: Time-to-live in seconds

        Returns:
            True if expired, False otherwise
        """
        return (time.time() - timestamp) > ttl

    def get_stats(self):
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats (size, oldest entry age, etc.)
        """
        with self.lock:
            if not self.cache:
                return {
                    'size': 0,
                    'oldest_entry_age': 0,
                    'newest_entry_age': 0
                }

            current_time = time.time()
            timestamps = [entry['timestamp'] for entry in self.cache.values()]

            return {
                'size': len(self.cache),
                'oldest_entry_age': int(current_time - min(timestamps)),
                'newest_entry_age': int(current_time - max(timestamps))
            }
