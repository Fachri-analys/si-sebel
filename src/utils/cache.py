"""
Redis caching system for Si Sebel Bot.
Provides distributed caching with Redis for improved performance.
"""

import json
from typing import Optional, Any, Union
from datetime import timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from .logger import Logger
from .exceptions import SiSebelException


class CacheError(SiSebelException):
    """Exception raised when cache operation fails."""
    pass


class CacheManager:
    """
    Redis cache manager for distributed caching.
    Handles caching of frequently accessed data to reduce database load.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str = None,
        ttl: int = 3600,
        enabled: bool = True,
        logger: Optional[Logger] = None
    ):
        """
        Initialize cache manager.

        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Redis password (optional)
            ttl: Default time-to-live for cache entries in seconds
            enabled: Whether caching is enabled
            logger: Logger instance
        """
        if not REDIS_AVAILABLE:
            if enabled:
                raise CacheError(
                    "Redis library not available. Install with: pip install redis"
                )
            self.enabled = False
            self.logger = logger or Logger.get_logger("cache_manager")
            self.logger.warning("Redis not available, caching disabled")
            return

        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.ttl = ttl
        self.enabled = enabled
        self.logger = logger or Logger.get_logger("cache_manager")
        
        self.redis_client: Optional[redis.Redis] = None

    def connect(self) -> bool:
        """
        Connect to Redis server.

        Returns:
            True if connection successful, False otherwise
        """
        if not self.enabled:
            self.logger.info("Caching is disabled")
            return False

        try:
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password if self.password else None,
                decode_responses=False,  # Handle binary data
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            self.redis_client.ping()
            self.logger.info(f"Connected to Redis at {self.host}:{self.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            self.enabled = False
            return False

    def disconnect(self) -> None:
        """Disconnect from Redis server."""
        if self.redis_client:
            try:
                self.redis_client.close()
                self.logger.info("Disconnected from Redis")
            except Exception as e:
                self.logger.error(f"Error disconnecting from Redis: {e}")
            finally:
                self.redis_client = None

    def _serialize(self, value: Any) -> bytes:
        """
        Serialize value for storage in Redis.

        Args:
            value: Value to serialize

        Returns:
            Serialized bytes
        """
        try:
            # Try JSON first (more readable)
            return json.dumps(value).encode('utf-8')
        except (TypeError, ValueError) as exc:
            raise CacheError("Cache values must be JSON serializable") from exc

    def _deserialize(self, value: bytes) -> Any:
        """
        Deserialize value from Redis.

        Args:
            value: Serialized bytes

        Returns:
            Deserialized value
        """
        try:
            # Try JSON first
            return json.loads(value.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise CacheError("Invalid cache payload") from exc

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.enabled or not self.redis_client:
            return None

        try:
            cached_value = self.redis_client.get(key)
            if cached_value is None:
                return None
            
            self.logger.debug(f"Cache hit for key: {key}")
            return self._deserialize(cached_value)
            
        except Exception as e:
            self.logger.error(f"Error getting from cache (key: {key}): {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if not specified)

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            serialized_value = self._serialize(value)
            cache_ttl = ttl if ttl is not None else self.ttl
            
            self.redis_client.setex(key, cache_ttl, serialized_value)
            self.logger.debug(f"Cached value for key: {key} (TTL: {cache_ttl}s)")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting cache (key: {key}): {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            self.redis_client.delete(key)
            self.logger.debug(f"Deleted cache for key: {key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting cache (key: {key}): {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.

        Args:
            pattern: Key pattern (e.g., "school_info:*")

        Returns:
            Number of keys deleted
        """
        if not self.enabled or not self.redis_client:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                self.logger.info(f"Deleted {deleted} keys matching pattern: {pattern}")
                return deleted
            return 0
            
        except Exception as e:
            self.logger.error(f"Error deleting pattern {pattern}: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            self.logger.error(f"Error checking cache existence (key: {key}): {e}")
            return False

    def clear_all(self) -> bool:
        """
        Clear all cached data.

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            self.redis_client.flushdb()
            self.logger.info("Cleared all cache data")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
            return False

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        if not self.enabled or not self.redis_client:
            return {"enabled": False}

        try:
            info = self.redis_client.info()
            return {
                "enabled": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "N/A"),
                "total_keys": self.redis_client.dbsize(),
                "hit_rate": info.get("keyspace_hits", 0) / max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1) * 100
            }
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {e}")
            return {"enabled": True, "error": str(e)}


class CacheKey:
    """Cache key generator for consistent key naming."""

    @staticmethod
    def school_info(key: str = None) -> str:
        """Generate cache key for school info."""
        return f"school_info:{key}" if key else "school_info:all"

    @staticmethod
    def jurusan(jurusan_id: int = None) -> str:
        """Generate cache key for jurusan."""
        return f"jurusan:{jurusan_id}" if jurusan_id else "jurusan:all"

    @staticmethod
    def faq(query: str = None) -> str:
        """Generate cache key for FAQ."""
        return f"faq:{query}" if query else "faq:popular"

    @staticmethod
    def calendar(event_type: str = None, tahun_ajaran: str = None) -> str:
        """Generate cache key for calendar."""
        parts = ["calendar"]
        if event_type:
            parts.append(event_type)
        if tahun_ajaran:
            parts.append(tahun_ajaran)
        return ":".join(parts)

    @staticmethod
    def contact(role: str = None) -> str:
        """Generate cache key for contacts."""
        return f"contact:{role}" if role else "contact:all"

    @staticmethod
    def facilities() -> str:
        """Generate cache key for facilities."""
        return "facilities:all"

    @staticmethod
    def extracurricular() -> str:
        """Generate cache key for extracurricular."""
        return "extracurricular:all"

    @staticmethod
    def ppdb_info(key: str = None, tahun_ajaran: str = None) -> str:
        """Generate cache key for PPDB info."""
        parts = ["ppdb"]
        if key:
            parts.append(key)
        if tahun_ajaran:
            parts.append(tahun_ajaran)
        return ":".join(parts)


# Global cache instance
_cache_instance: Optional[CacheManager] = None


def get_cache_manager(
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    password: str = None,
    ttl: int = 3600,
    enabled: bool = True,
    logger: Optional[Logger] = None
) -> CacheManager:
    """
    Get or create cache manager instance.

    Args:
        host: Redis server host
        port: Redis server port
        db: Redis database number
        password: Redis password
        ttl: Default time-to-live
        enabled: Whether caching is enabled
        logger: Logger instance

    Returns:
        CacheManager instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager(
            host=host,
            port=port,
            db=db,
            password=password,
            ttl=ttl,
            enabled=enabled,
            logger=logger
        )
    return _cache_instance