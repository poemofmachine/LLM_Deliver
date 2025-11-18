"""
캐싱 유틸리티 모듈

FastAPI 엔드포인트를 위한 다양한 캐싱 전략:
- 함수 레벨 LRU 캐싱 (메모리 효율적)
- TTL 기반 캐싱 (시간 제한)
- 조건부 캐싱 (특정 조건에서만 캐시)
"""

import time
import hashlib
import json
from typing import Any, Callable, Optional, TypeVar, ParamSpec
from functools import wraps
from collections import OrderedDict
from threading import Lock
import asyncio

T = TypeVar('T')
P = ParamSpec('P')


# ============================================================================
# LRU 캐시 구현
# ============================================================================

class LRUCache:
    """제한된 크기의 LRU (Least Recently Used) 캐시"""

    def __init__(self, maxsize: int = 128):
        """
        Args:
            maxsize: 캐시의 최대 항목 수
        """
        self.maxsize = maxsize
        self.cache: OrderedDict = OrderedDict()
        self.lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        with self.lock:
            if key not in self.cache:
                return None
            # LRU를 위해 최근에 사용한 항목을 끝으로 이동
            self.cache.move_to_end(key)
            return self.cache[key]

    def set(self, key: str, value: Any) -> None:
        """캐시에 값 저장"""
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            # 크기 제한 초과 시 가장 오래된 항목 삭제
            if len(self.cache) > self.maxsize:
                self.cache.popitem(last=False)

    def clear(self) -> None:
        """캐시 비우기"""
        with self.lock:
            self.cache.clear()

    def get_stats(self) -> dict:
        """캐시 통계"""
        return {
            "size": len(self.cache),
            "maxsize": self.maxsize,
            "usage_percent": (len(self.cache) / self.maxsize) * 100
        }


# ============================================================================
# TTL 캐시 구현
# ============================================================================

class TTLCache:
    """TTL (Time To Live) 기반 캐시"""

    def __init__(self, ttl_seconds: int = 3600):
        """
        Args:
            ttl_seconds: 캐시 항목의 유효 시간 (초)
        """
        self.ttl = ttl_seconds
        self.cache: dict = {}
        self.timestamps: dict = {}
        self.lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회 (유효 기간 확인)"""
        with self.lock:
            if key not in self.cache:
                return None

            # TTL 확인
            if time.time() - self.timestamps[key] > self.ttl:
                del self.cache[key]
                del self.timestamps[key]
                return None

            return self.cache[key]

    def set(self, key: str, value: Any) -> None:
        """캐시에 값 저장"""
        with self.lock:
            self.cache[key] = value
            self.timestamps[key] = time.time()

    def clear(self) -> None:
        """캐시 비우기"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()

    def cleanup_expired(self) -> int:
        """만료된 항목 정리"""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self.timestamps.items()
            if current_time - timestamp > self.ttl
        ]
        with self.lock:
            for key in expired_keys:
                del self.cache[key]
                del self.timestamps[key]
        return len(expired_keys)

    def get_stats(self) -> dict:
        """캐시 통계"""
        return {
            "size": len(self.cache),
            "ttl_seconds": self.ttl,
            "expired_count": self.cleanup_expired()
        }


# ============================================================================
# 글로벌 캐시 인스턴스
# ============================================================================

# 기본 LRU 캐시 (128 항목)
_lru_cache = LRUCache(maxsize=128)

# 1시간 TTL 캐시
_ttl_cache_1h = TTLCache(ttl_seconds=3600)

# 5분 TTL 캐시
_ttl_cache_5m = TTLCache(ttl_seconds=300)


# ============================================================================
# 캐시 키 생성 함수
# ============================================================================

def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    함수 인자를 기반으로 캐시 키 생성

    Args:
        prefix: 캐시 키 접두어
        *args: 위치 인자
        **kwargs: 키워드 인자

    Returns:
        생성된 캐시 키
    """
    key_data = {
        'prefix': prefix,
        'args': args,
        'kwargs': kwargs
    }
    key_str = json.dumps(key_data, default=str, sort_keys=True)
    key_hash = hashlib.md5(key_str.encode()).hexdigest()
    return f"{prefix}:{key_hash}"


# ============================================================================
# 데코레이터
# ============================================================================

def cache_result(
    ttl: Optional[int] = 3600,
    maxsize: int = 128,
    key_prefix: Optional[str] = None
):
    """
    함수 결과를 캐싱하는 데코레이터

    Args:
        ttl: TTL (초), None이면 무제한
        maxsize: LRU 캐시 최대 크기
        key_prefix: 캐시 키 접두어

    Example:
        @cache_result(ttl=300)
        async def get_memories(scope: str):
            return storage.list_memories(scope=scope)
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        prefix = key_prefix or func.__name__
        cache = TTLCache(ttl) if ttl else LRUCache(maxsize)

        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            # 캐시 키 생성
            cache_key = generate_cache_key(prefix, *args, **kwargs)

            # 캐시 조회
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # 함수 실행
            result = await func(*args, **kwargs)

            # 캐시 저장
            cache.set(cache_key, result)
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            # 캐시 키 생성
            cache_key = generate_cache_key(prefix, *args, **kwargs)

            # 캐시 조회
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # 함수 실행
            result = func(*args, **kwargs)

            # 캐시 저장
            cache.set(cache_key, result)
            return result

        # 비동기/동기 함수 선택
        wrapper = async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        wrapper.cache = cache  # 캐시 객체 노출 (테스트/모니터링용)
        return wrapper

    return decorator


def cache_read_only(ttl: int = 3600):
    """
    읽기 전용(GET) 엔드포인트를 위한 캐싱 데코레이터

    Args:
        ttl: TTL (초)

    Example:
        @router.get("/memories")
        @cache_read_only(ttl=300)
        async def list_memories(scope: str):
            return storage.list_memories(scope=scope)
    """
    return cache_result(ttl=ttl)


def cache_invalidate(*prefixes: str):
    """
    캐시 무효화 함수

    Args:
        *prefixes: 무효화할 캐시 키 접두어

    Example:
        @cache_invalidate("list_memories", "get_memory")
        async def save_memory(content: str):
            storage.save_memory(content)
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            result = await func(*args, **kwargs)
            # 모든 캐시 비우기 (간단한 구현)
            _lru_cache.clear()
            _ttl_cache_1h.clear()
            _ttl_cache_5m.clear()
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            result = func(*args, **kwargs)
            # 모든 캐시 비우기 (간단한 구현)
            _lru_cache.clear()
            _ttl_cache_1h.clear()
            _ttl_cache_5m.clear()
            return result

        wrapper = async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return wrapper

    return decorator


# ============================================================================
# 캐시 관리 함수
# ============================================================================

def get_cache_stats() -> dict:
    """모든 캐시의 통계 반환"""
    return {
        "lru_cache": _lru_cache.get_stats(),
        "ttl_cache_1h": _ttl_cache_1h.get_stats(),
        "ttl_cache_5m": _ttl_cache_5m.get_stats(),
    }


def clear_all_caches() -> dict:
    """모든 캐시 비우기"""
    _lru_cache.clear()
    _ttl_cache_1h.clear()
    _ttl_cache_5m.clear()
    return {"status": "all caches cleared"}


def cleanup_expired_caches() -> dict:
    """만료된 캐시 항목 정리"""
    expired_1h = _ttl_cache_1h.cleanup_expired()
    expired_5m = _ttl_cache_5m.cleanup_expired()
    return {
        "expired_1h": expired_1h,
        "expired_5m": expired_5m,
        "total_expired": expired_1h + expired_5m
    }
