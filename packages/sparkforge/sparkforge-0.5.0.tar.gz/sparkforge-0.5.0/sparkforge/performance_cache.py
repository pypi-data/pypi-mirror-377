#!/usr/bin/env python3
# # # # Copyright (c) 2024 Odos Matthews
# # # #
# # # # Permission is hereby granted, free of charge, to any person obtaining a copy
# # # # of this software and associated documentation files (the "Software"), to deal
# # # # in the Software without restriction, including without limitation the rights
# # # # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# # # # copies of the Software, and to permit persons to whom the Software is
# # # # furnished to do so, subject to the following conditions:
# # # #
# # # # The above copyright notice and this permission notice shall be included in all
# # # # copies or substantial portions of the Software.
# # # #
# # # # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# # # # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# # # # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# # # # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# # # # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# # # # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# # # # SOFTWARE.
# #
# # # Copyright (c) 2024 Odos Matthews
# # #
# # # Permission is hereby granted, free of charge, to any person obtaining a copy
# # # of this software and associated documentation files (the "Software"), to deal
# # # in the Software without restriction, including without limitation the rights
# # # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# # # copies of the Software, and to permit persons to whom the Software is
# # # furnished to do so, subject to the following conditions:
# # #
# # # The above copyright notice and this permission notice shall be included in all
# # # copies or substantial portions of the Software.
# # #
# # # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# # # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# # # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# # # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# # # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# # # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# # # SOFTWARE.
#
# # # Copyright (c) 2024 Odos Matthews
# # #
# # # Permission is hereby granted, free of charge, to any person obtaining a copy
# # # of this software and associated documentation files (the "Software"), to deal
# # # in the Software without restriction, including without limitation the rights
# # # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# # # copies of the Software, and to permit persons to whom the Software is
# # # furnished to do so, subject to the following conditions:
# # #
# # # The above copyright notice and this permission notice shall be included in all
# # # copies or substantial portions of the Software.
# # #
# # # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# # # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# # # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# # # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# # # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# # # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# # # SOFTWARE.
#
# # Copyright (c) 2024 Odos Matthews
# #
# # Permission is hereby granted, free of charge, to any person obtaining a copy
# # of this software and associated documentation files (the "Software"), to deal
# # in the Software without restriction, including without limitation the rights
# # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# # copies of the Software, and to permit persons to whom the Software is
# # furnished to do so, subject to the following conditions:
# #
# # The above copyright notice and this permission notice shall be included in all
# # copies or substantial portions of the Software.
# #
# # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# # SOFTWARE.

#


"""
Performance caching utilities for SparkForge pipeline framework.

This module provides intelligent caching mechanisms to optimize pipeline performance
by reducing redundant computations and improving memory management.

Key Features:
- DataFrame caching with TTL
- Validation result caching
- Memory management and cleanup
- Performance monitoring
- Cache invalidation strategies
"""

from __future__ import annotations

import hashlib
import logging
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable

from pyspark.sql import DataFrame

from .constants import BYTES_PER_MB, DEFAULT_MAX_MEMORY_MB


class CacheStrategy(Enum):
    """Cache strategies for different data types."""

    LRU = "lru"  # Least Recently Used
    TTL = "ttl"  # Time To Live
    SIZE = "size"  # Size-based eviction
    MANUAL = "manual"  # Manual invalidation only


@dataclass
class CacheConfig:
    """Configuration for caching system."""

    max_cache_size: int = 100  # Maximum number of cached items
    max_memory_mb: int = DEFAULT_MAX_MEMORY_MB  # Maximum memory usage in MB
    default_ttl_seconds: int = 3600  # Default TTL for cached items
    enable_validation_cache: bool = True
    enable_dataframe_cache: bool = True
    enable_rule_cache: bool = True
    cleanup_interval_seconds: int = 300  # Cleanup interval
    enable_compression: bool = True
    enable_persistence: bool = False
    cache_directory: str = "/tmp/sparkforge_cache"


@dataclass
class CacheEntry:
    """A single cache entry."""

    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    size_bytes: int = 0
    ttl_seconds: int | None = None
    strategy: CacheStrategy = CacheStrategy.LRU

    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.ttl_seconds is None:
            return False
        return (datetime.utcnow() - self.created_at).total_seconds() > self.ttl_seconds

    @property
    def age_seconds(self) -> float:
        """Get age of cache entry in seconds."""
        return (datetime.utcnow() - self.created_at).total_seconds()


class PerformanceCache:
    """High-performance caching system for SparkForge."""

    def __init__(self, config: CacheConfig | None = None):
        """Initialize performance cache."""
        self.config = config or CacheConfig()
        self.logger = logging.getLogger(__name__)
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
        self.stats = {"hits": 0, "misses": 0, "evictions": 0, "total_size_bytes": 0}

        # Start cleanup thread
        if self.config.cleanup_interval_seconds > 0:
            self._start_cleanup_thread()

    def get(self, key: str) -> Any | None:
        """Get value from cache."""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]

                # Check if expired
                if entry.is_expired:
                    self._remove_entry(key)
                    self.stats["misses"] += 1
                    return None

                # Update access info
                entry.last_accessed = datetime.utcnow()
                entry.access_count += 1

                # Move to end (most recently used)
                self.cache.move_to_end(key)

                self.stats["hits"] += 1
                return entry.value
            else:
                self.stats["misses"] += 1
                return None

    def put(
        self,
        key: str,
        value: Any,
        ttl_seconds: int | None = None,
        strategy: CacheStrategy = CacheStrategy.LRU,
    ) -> None:
        """Put value in cache."""
        with self.lock:
            # Calculate size
            size_bytes = self._calculate_size(value)

            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                size_bytes=size_bytes,
                ttl_seconds=ttl_seconds or self.config.default_ttl_seconds,
                strategy=strategy,
            )

            # Remove existing entry if it exists
            if key in self.cache:
                self._remove_entry(key)

            # Add new entry
            self.cache[key] = entry
            self.stats["total_size_bytes"] += size_bytes

            # Check if we need to evict
            self._evict_if_needed()

    def invalidate(self, key: str) -> bool:
        """Invalidate cache entry."""
        with self.lock:
            if key in self.cache:
                self._remove_entry(key)
                return True
            return False

    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            self.stats["total_size_bytes"] = 0

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            hit_rate = 0.0
            total_requests = self.stats["hits"] + self.stats["misses"]
            if total_requests > 0:
                hit_rate = self.stats["hits"] / total_requests

            return {
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "hit_rate": hit_rate,
                "evictions": self.stats["evictions"],
                "total_size_bytes": self.stats["total_size_bytes"],
                "total_size_mb": self.stats["total_size_bytes"] / BYTES_PER_MB,
                "entry_count": len(self.cache),
                "max_size": self.config.max_cache_size,
                "max_memory_mb": self.config.max_memory_mb,
            }

    def _remove_entry(self, key: str) -> None:
        """Remove cache entry."""
        if key in self.cache:
            entry = self.cache[key]
            self.stats["total_size_bytes"] -= entry.size_bytes
            del self.cache[key]

    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of value in bytes."""
        if isinstance(value, DataFrame):
            # For DataFrames, estimate size based on row count and schema
            try:
                row_count: int = value.count()
                column_count: int = len(value.columns)
                # Rough estimate: 100 bytes per row per column
                return row_count * column_count * 100
            except Exception:
                return DEFAULT_MAX_MEMORY_MB  # Default estimate
        elif isinstance(value, (str, int, float, bool)):
            return len(str(value))
        elif isinstance(value, (list, tuple)):
            return sum(self._calculate_size(item) for item in value)
        elif isinstance(value, dict):
            return sum(
                self._calculate_size(k) + self._calculate_size(v)
                for k, v in value.items()
            )
        else:
            return DEFAULT_MAX_MEMORY_MB  # Default estimate

    def _evict_if_needed(self) -> None:
        """Evict entries if cache limits are exceeded."""
        # Check size limit
        while len(self.cache) > self.config.max_cache_size:
            self._evict_lru()

        # Check memory limit
        while (
            self.stats["total_size_bytes"] > self.config.max_memory_mb * BYTES_PER_MB
            and len(self.cache) > 0
        ):
            self._evict_lru()

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if self.cache:
            # Remove first item (least recently used)
            key, entry = self.cache.popitem(last=False)
            self.stats["total_size_bytes"] -= entry.size_bytes
            self.stats["evictions"] += 1

    def _start_cleanup_thread(self) -> None:
        """Start background cleanup thread."""

        def cleanup_worker() -> None:
            while True:
                time.sleep(self.config.cleanup_interval_seconds)
                self._cleanup_expired()

        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()

    def _cleanup_expired(self) -> None:
        """Clean up expired entries."""
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items() if entry.is_expired
            ]
            for key in expired_keys:
                self._remove_entry(key)


class ValidationCache:
    """Specialized cache for validation results."""

    def __init__(self, cache: PerformanceCache):
        """Initialize validation cache."""
        self.cache = cache
        self.logger = logging.getLogger(__name__)

    def get_validation_result(
        self, df_hash: str, rules_hash: str
    ) -> dict[str, Any] | None:
        """Get cached validation result."""
        key = f"validation:{df_hash}:{rules_hash}"
        return self.cache.get(key)

    def put_validation_result(
        self, df_hash: str, rules_hash: str, result: dict[str, Any]
    ) -> None:
        """Cache validation result."""
        key = f"validation:{df_hash}:{rules_hash}"
        self.cache.put(key, result, ttl_seconds=1800)  # 30 minutes TTL

    def get_dataframe_hash(self, df: DataFrame) -> str:
        """Get hash for DataFrame (schema + sample data)."""
        try:
            # Get schema hash
            schema_str = str(df.schema)

            # Get sample data hash (first 100 rows)
            sample_df = df.limit(100)
            sample_data = sample_df.collect()
            sample_str = str(sample_data)

            # Combine and hash
            combined = f"{schema_str}:{sample_str}"
            return hashlib.md5(combined.encode()).hexdigest()
        except Exception as e:
            self.logger.warning(f"Failed to generate DataFrame hash: {e}")
            return hashlib.md5(str(time.time()).encode()).hexdigest()

    def get_rules_hash(self, rules: dict[str, list[Any]]) -> str:
        """Get hash for validation rules."""
        rules_str = str(sorted(rules.items()))
        return hashlib.md5(rules_str.encode()).hexdigest()


def cached_validation(func: Callable) -> Callable:
    """Decorator to cache validation results."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Extract DataFrame and rules from arguments
        df = args[0] if args else None
        rules = args[1] if len(args) > 1 else kwargs.get("rules")

        if df is None or rules is None:
            return func(*args, **kwargs)

        # Get cache
        cache = get_performance_cache()
        validation_cache = ValidationCache(cache)

        # Generate hashes
        df_hash = validation_cache.get_dataframe_hash(df)
        rules_hash = validation_cache.get_rules_hash(rules)

        # Check cache
        cached_result = validation_cache.get_validation_result(df_hash, rules_hash)
        if cached_result:
            return cached_result

        # Execute function and cache result
        result = func(*args, **kwargs)
        validation_cache.put_validation_result(df_hash, rules_hash, result)

        return result

    return wrapper


def cached_dataframe(ttl_seconds: int = 3600) -> Callable:
    """Decorator to cache DataFrame operations."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key from function name and arguments
            key_parts = [func.__name__]
            for arg in args:
                if isinstance(arg, DataFrame):
                    key_parts.append(f"df:{hash(str(arg.schema))}")
                else:
                    key_parts.append(str(arg))
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))

            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()

            # Get cache
            cache = get_performance_cache()
            cached_result = cache.get(cache_key)

            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.put(cache_key, result, ttl_seconds=ttl_seconds)

            return result

        return wrapper

    return decorator


# Global cache instance
_performance_cache: PerformanceCache | None = None


def get_performance_cache() -> PerformanceCache:
    """Get global performance cache instance."""
    global _performance_cache
    if _performance_cache is None:
        _performance_cache = PerformanceCache()
    return _performance_cache


def clear_performance_cache() -> None:
    """Clear global performance cache."""
    global _performance_cache
    if _performance_cache:
        _performance_cache.clear()


def get_cache_stats() -> dict[str, Any]:
    """Get performance cache statistics."""
    cache = get_performance_cache()
    return cache.get_stats()
