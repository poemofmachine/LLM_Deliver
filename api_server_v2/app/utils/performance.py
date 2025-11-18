"""
성능 모니터링 및 벤치마킹 모듈

API 성능 추적 및 모니터링을 위한 유틸리티:
- 요청 성능 측정
- 엔드포인트별 통계 수집
- 성능 임계값 모니터링
"""

import time
import statistics
from typing import Dict, List, Optional, Callable, TypeVar, ParamSpec
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
import asyncio

T = TypeVar('T')
P = ParamSpec('P')


# ============================================================================
# 데이터 클래스
# ============================================================================

@dataclass
class PerformanceMetrics:
    """성능 지표"""
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EndpointStats:
    """엔드포인트 통계"""
    endpoint: str
    method: str
    request_count: int = 0
    total_time_ms: float = 0.0
    min_time_ms: float = float('inf')
    max_time_ms: float = 0.0
    error_count: int = 0
    status_codes: Dict[int, int] = field(default_factory=dict)

    @property
    def avg_time_ms(self) -> float:
        """평균 응답 시간"""
        return self.total_time_ms / self.request_count if self.request_count > 0 else 0

    @property
    def success_rate(self) -> float:
        """성공률 (200-299)"""
        success_count = sum(
            count for code, count in self.status_codes.items()
            if 200 <= code < 300
        )
        return (success_count / self.request_count * 100) if self.request_count > 0 else 0


# ============================================================================
# 성능 모니터 (싱글톤)
# ============================================================================

class PerformanceMonitor:
    """API 성능 모니터링"""

    _instance = None
    _metrics: List[PerformanceMetrics] = []
    _stats: Dict[str, EndpointStats] = {}
    _threshold_ms: float = 1000.0  # 성능 경고 임계값 (ms)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def record_metric(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float
    ) -> None:
        """성능 지표 기록"""
        # 지표 저장
        metric = PerformanceMetrics(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms
        )
        self._metrics.append(metric)

        # 통계 업데이트
        key = f"{method} {endpoint}"
        if key not in self._stats:
            self._stats[key] = EndpointStats(endpoint=endpoint, method=method)

        stats = self._stats[key]
        stats.request_count += 1
        stats.total_time_ms += response_time_ms
        stats.min_time_ms = min(stats.min_time_ms, response_time_ms)
        stats.max_time_ms = max(stats.max_time_ms, response_time_ms)

        # 상태 코드 통계
        stats.status_codes[status_code] = stats.status_codes.get(status_code, 0) + 1

        # 에러 처리
        if status_code >= 400:
            stats.error_count += 1

        # 성능 경고
        if response_time_ms > self._threshold_ms:
            print(
                f"⚠️ 성능 경고: {method} {endpoint} - "
                f"{response_time_ms:.2f}ms (임계값: {self._threshold_ms}ms)"
            )

    def get_endpoint_stats(self, endpoint: Optional[str] = None) -> Dict[str, EndpointStats]:
        """엔드포인트 통계 조회"""
        if endpoint:
            return {
                k: v for k, v in self._stats.items()
                if endpoint in k
            }
        return self._stats

    def get_slowest_endpoints(self, count: int = 5) -> List[tuple]:
        """가장 느린 엔드포인트 조회"""
        sorted_stats = sorted(
            self._stats.items(),
            key=lambda x: x[1].avg_time_ms,
            reverse=True
        )
        return sorted_stats[:count]

    def get_most_used_endpoints(self, count: int = 5) -> List[tuple]:
        """가장 많이 사용된 엔드포인트 조회"""
        sorted_stats = sorted(
            self._stats.items(),
            key=lambda x: x[1].request_count,
            reverse=True
        )
        return sorted_stats[:count]

    def get_summary(self) -> dict:
        """전체 성능 요약"""
        total_requests = sum(s.request_count for s in self._stats.values())
        total_errors = sum(s.error_count for s in self._stats.values())
        avg_response_time = (
            statistics.mean(m.response_time_ms for m in self._metrics)
            if self._metrics else 0
        )

        return {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate_percent": (total_errors / total_requests * 100) if total_requests > 0 else 0,
            "avg_response_time_ms": round(avg_response_time, 2),
            "endpoint_count": len(self._stats),
            "last_metric_time": self._metrics[-1].timestamp if self._metrics else None
        }

    def reset(self) -> None:
        """모니터 리셋"""
        self._metrics.clear()
        self._stats.clear()


# ============================================================================
# 글로벌 모니터 인스턴스
# ============================================================================

_monitor = PerformanceMonitor()


# ============================================================================
# 데코레이터
# ============================================================================

def track_performance(threshold_ms: float = 1000.0):
    """
    엔드포인트 성능을 추적하는 데코레이터

    Args:
        threshold_ms: 성능 경고 임계값 (ms)

    Example:
        @app.get("/memories")
        @track_performance(threshold_ms=500)
        async def list_memories():
            return storage.list_memories()
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            start_time = time.time()
            status_code = 200
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status_code = 500
                raise
            finally:
                response_time_ms = (time.time() - start_time) * 1000
                endpoint = func.__name__
                method = "ASYNC"
                _monitor.record_metric(endpoint, method, status_code, response_time_ms)

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            start_time = time.time()
            status_code = 200
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status_code = 500
                raise
            finally:
                response_time_ms = (time.time() - start_time) * 1000
                endpoint = func.__name__
                method = "SYNC"
                _monitor.record_metric(endpoint, method, status_code, response_time_ms)

        wrapper = async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return wrapper

    return decorator


def measure_time(operation_name: str = "operation"):
    """
    코드 블록의 실행 시간을 측정하는 컨텍스트 매니저

    Example:
        with measure_time("메모리 저장"):
            storage.save_memory(content)
    """
    class TimeMeasure:
        def __enter__(self):
            self.start = time.time()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            elapsed_ms = (time.time() - self.start) * 1000
            status = "실패" if exc_type else "성공"
            print(f"⏱️  {operation_name}: {elapsed_ms:.2f}ms ({status})")

    return TimeMeasure()


# ============================================================================
# 모니터 접근 함수
# ============================================================================

def get_performance_stats() -> dict:
    """모든 성능 통계 조회"""
    return {
        "summary": _monitor.get_summary(),
        "endpoints": {
            k: {
                "request_count": v.request_count,
                "avg_time_ms": round(v.avg_time_ms, 2),
                "min_time_ms": round(v.min_time_ms, 2),
                "max_time_ms": round(v.max_time_ms, 2),
                "error_count": v.error_count,
                "success_rate_percent": round(v.success_rate, 2),
                "status_codes": v.status_codes
            }
            for k, v in _monitor.get_endpoint_stats().items()
        }
    }


def get_slowest_endpoints(count: int = 5) -> List[dict]:
    """가장 느린 엔드포인트 조회"""
    return [
        {
            "endpoint": f"{stats[1].method} {stats[1].endpoint}",
            "avg_time_ms": round(stats[1].avg_time_ms, 2),
            "request_count": stats[1].request_count
        }
        for stats in _monitor.get_slowest_endpoints(count)
    ]


def get_most_used_endpoints(count: int = 5) -> List[dict]:
    """가장 많이 사용된 엔드포인트 조회"""
    return [
        {
            "endpoint": f"{stats[1].method} {stats[1].endpoint}",
            "request_count": stats[1].request_count,
            "avg_time_ms": round(stats[1].avg_time_ms, 2),
            "success_rate_percent": round(stats[1].success_rate, 2)
        }
        for stats in _monitor.get_most_used_endpoints(count)
    ]


def reset_performance_stats() -> dict:
    """성능 통계 리셋"""
    _monitor.reset()
    return {"status": "performance stats reset"}
