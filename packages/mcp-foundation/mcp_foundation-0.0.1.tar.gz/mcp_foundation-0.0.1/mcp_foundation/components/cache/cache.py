import asyncio
import time
import json
import logging
import hashlib
from functools import wraps
from typing import Any, Dict, Optional, Callable
from ..base_component import BaseComponent

logger = logging.getLogger(__name__)

class SimpleCacheManager:
    """Simple in-memory cache manager for POC/demo purposes."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, Any] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        
        # Simple metrics
        self.hits = 0
        self.misses = 0
        self.sets = 0
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self._lock:
            if key not in self._cache:
                self.misses += 1
                logger.debug(f"Cache miss: {key}")
                return None
            
            # Check if expired
            metadata = self._metadata[key]
            if time.time() > metadata['expires_at']:
                # Expired, remove it
                del self._cache[key]
                del self._metadata[key]
                self.misses += 1
                logger.debug(f"Cache expired: {key}")
                return None
            
            # Cache hit
            self.hits += 1
            metadata['last_access'] = time.time()
            logger.debug(f"Cache hit: {key}")
            return self._cache[key]
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        ttl = ttl or self.default_ttl
        
        async with self._lock:
            # If at max size, remove oldest entry
            if len(self._cache) >= self.max_size and key not in self._cache:
                oldest_key = min(
                    self._metadata.keys(),
                    key=lambda k: self._metadata[k]['created_at']
                )
                del self._cache[oldest_key]
                del self._metadata[oldest_key]
                logger.debug(f"Cache evicted oldest: {oldest_key}")
            
            # Store value and metadata
            self._cache[key] = value
            self._metadata[key] = {
                'created_at': time.time(),
                'expires_at': time.time() + ttl,
                'last_access': time.time(),
                'ttl': ttl
            }
            
            self.sets += 1
            logger.debug(f"Cache set: {key} (ttl={ttl}s)")
            return True
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                del self._metadata[key]
                logger.debug(f"Cache delete: {key}")
                return True
            return False
    
    async def clear(self) -> int:
        """Clear all cache entries."""
        async with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._metadata.clear()
            logger.info(f"Cache cleared: {count} entries")
            return count
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "enabled": True,
            "type": "memory",
            "entries": len(self._cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "hit_rate": round(hit_rate, 2),
            "memory_usage": "simple"
        }

# Global cache instance
_cache_manager: Optional[SimpleCacheManager] = None

def get_cache() -> SimpleCacheManager:
    """Get global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = SimpleCacheManager()
    return _cache_manager

def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Simple caching decorator for async functions.
    
    Args:
        ttl: Time to live in seconds (uses cache default if None)
        key_prefix: Prefix for cache key
    
    Example:
        @cached(ttl=60, key_prefix="math")
        async def expensive_calculation(x, y):
            return x * y
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Generate cache key from function name and arguments
            key_parts = [key_prefix, func.__name__, str(args), str(sorted(kwargs.items()))]
            key_string = ":".join(str(part) for part in key_parts if part)
            cache_key = hashlib.md5(key_string.encode()).hexdigest()
            
            # Try to get from cache first
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Using cached result for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {func.__name__}")
            return result
        
        return wrapper
    return decorator

class CacheComponent(BaseComponent):
    name = "cache"

    def register(self, server, config=None):
        """Register cache component with the server."""
        if not config or not config.cache or not config.cache.enabled:
            logger.info("Cache component: disabled")
            return
        
        # Initialize cache with config values
        cache_config = config.cache
        global _cache_manager
        _cache_manager = SimpleCacheManager(
            max_size=cache_config.memory_max_size,
            default_ttl=cache_config.default_ttl
        )
        
        # Add cache utilities to server (if FastMCP supports this)
        if hasattr(server, '_cache'):
            server._cache = _cache_manager
        
        logger.info(f"✅ Cache component registered - max_size: {cache_config.memory_max_size}, default_ttl: {cache_config.default_ttl}s")
