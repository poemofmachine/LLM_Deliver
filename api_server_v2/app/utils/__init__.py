"""
유틸리티 모듈

캐싱, 성능 모니터링, 보안 및 기타 공용 함수 제공
"""

from .cache import (
    LRUCache,
    TTLCache,
    cache_result,
    cache_read_only,
    cache_invalidate,
    get_cache_stats,
    clear_all_caches,
    cleanup_expired_caches,
    generate_cache_key
)

from .performance import (
    PerformanceMonitor,
    PerformanceMetrics,
    EndpointStats,
    track_performance,
    measure_time,
    get_performance_stats,
    get_slowest_endpoints,
    get_most_used_endpoints,
    reset_performance_stats,
)

__all__ = [
    # Cache utilities
    "LRUCache",
    "TTLCache",
    "cache_result",
    "cache_read_only",
    "cache_invalidate",
    "get_cache_stats",
    "clear_all_caches",
    "cleanup_expired_caches",
    "generate_cache_key",
    # Performance utilities
    "PerformanceMonitor",
    "PerformanceMetrics",
    "EndpointStats",
    "track_performance",
    "measure_time",
    "get_performance_stats",
    "get_slowest_endpoints",
    "get_most_used_endpoints",
    "reset_performance_stats",
]
