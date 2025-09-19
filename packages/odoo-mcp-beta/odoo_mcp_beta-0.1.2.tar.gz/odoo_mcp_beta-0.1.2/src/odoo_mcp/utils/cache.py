"""
Caching utilities for Odoo MCP to improve performance
"""

import time
import hashlib
import json
from typing import Any, Optional, Dict
from functools import wraps


class SimpleCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, default_ttl: int = 300):
        """
        Initialize cache
        
        Args:
            default_ttl: Default time-to-live in seconds (5 minutes)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def _make_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key in self._cache:
            entry = self._cache[key]
            if time.time() < entry['expires']:
                return entry['value']
            else:
                # Remove expired entry
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        ttl = ttl or self.default_ttl
        self._cache[key] = {
            'value': value,
            'expires': time.time() + ttl
        }
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
    
    def cleanup(self) -> None:
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time >= entry['expires']
        ]
        for key in expired_keys:
            del self._cache[key]


# Global cache instance
_cache = SimpleCache()


def cached(ttl: int = 300):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time-to-live in seconds
    
    Example:
        @cached(ttl=600)
        def get_expensive_data(model, domain):
            return odoo.search_read(model, domain)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__module__}.{func.__name__}:{_cache._make_key(*args, **kwargs)}"
            
            # Check cache
            cached_value = _cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            _cache.set(cache_key, result, ttl)
            return result
        
        # Add cache control methods
        wrapper.clear_cache = lambda: _cache.clear()
        wrapper.cache_key = lambda *a, **kw: f"{func.__module__}.{func.__name__}:{_cache._make_key(*a, **kw)}"
        
        return wrapper
    return decorator


class ModelCache:
    """Cache specifically for Odoo model data"""
    
    def __init__(self, ttl: int = 300):
        self.cache = SimpleCache(default_ttl=ttl)
        self.model_versions: Dict[str, int] = {}
    
    def get_model_data(self, model: str, key: str) -> Optional[Any]:
        """Get cached model data"""
        cache_key = f"{model}:{key}"
        return self.cache.get(cache_key)
    
    def set_model_data(self, model: str, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set model data in cache"""
        cache_key = f"{model}:{key}"
        self.cache.set(cache_key, value, ttl)
    
    def invalidate_model(self, model: str) -> None:
        """Invalidate all cache entries for a model"""
        keys_to_remove = [
            key for key in self.cache._cache.keys()
            if key.startswith(f"{model}:")
        ]
        for key in keys_to_remove:
            del self.cache._cache[key]
    
    def get_fields(self, model: str) -> Optional[Dict]:
        """Get cached field definitions"""
        return self.get_model_data(model, 'fields')
    
    def set_fields(self, model: str, fields: Dict, ttl: int = 3600) -> None:
        """Cache field definitions (1 hour default)"""
        self.set_model_data(model, 'fields', fields, ttl)
    
    def get_metadata(self, model: str) -> Optional[Dict]:
        """Get cached model metadata"""
        return self.get_model_data(model, 'metadata')
    
    def set_metadata(self, model: str, metadata: Dict, ttl: int = 3600) -> None:
        """Cache model metadata (1 hour default)"""
        self.set_model_data(model, 'metadata', metadata, ttl)


# Global model cache instance
model_cache = ModelCache()


def clear_all_caches():
    """Clear all caches"""
    _cache.clear()
    model_cache.cache.clear()