"""
Memory Hub v2 - FastAPI 메인 애플리케이션

⚡ 성능 최적화:
- GZip 응답 압축 (1000 바이트 이상)
- CORS 미들웨어 최적화
- 모든 라우터를 비동기(async/await) 엔드포인트로 등록
- 신뢰된 호스트 설정
- 에러 처리 미들웨어
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
from contextlib import asynccontextmanager

from .config import settings
from .routes import sessions, tokens, workspaces, superthread, google_docs
from .routes import auth  # 1. 방금 만든 auth 라우터 임포트
from .utils import (
    get_performance_stats,
    get_slowest_endpoints,
    get_most_used_endpoints,
    reset_performance_stats,
    get_cache_stats,
    clear_all_caches,
    cleanup_expired_caches,
)


# ============================================================================
# 앱 초기화 및 라이프사이클 이벤트
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 함수"""
    # 앱 시작 시
    print("🚀 Memory Hub v2 시작")
    print("⚡ 성능 최적화 활성화: async endpoints, GZip compression, caching")
    yield
    # 앱 종료 시
    print("🛑 Memory Hub v2 종료")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Reference FastAPI implementation for Memory Hub v2 - Performance Optimized",
    lifespan=lifespan
)

# ============================================================================
# 미들웨어 설정 (성능 최적화)
# ============================================================================

# 1. GZip 응답 압축 (1000바이트 이상의 응답을 압축)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 2. CORS 설정 (프로덕션에서는 origins를 더 제한)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. 신뢰된 호스트 설정 (XXE 방지)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.example.com"]
)

# ============================================================================
# 라우터 등록
# ============================================================================

app.include_router(workspaces.router)
app.include_router(sessions.router)
app.include_router(tokens.router)
app.include_router(auth.router)  # 2. auth 라우터 포함
app.include_router(superthread.router)  # 3. superthread 라우터 포함 (async endpoints)
app.include_router(google_docs.router)  # 4. google_docs 라우터 포함 (async endpoints)


# ============================================================================
# 헬스 체크 엔드포인트
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """애플리케이션 헬스 체크"""
    return {
        "status": "ok",
        "version": "0.1.0",
        "optimizations": [
            "async/await endpoints",
            "gzip compression",
            "caching support",
            "cors enabled",
            "trusted hosts configured"
        ]
    }


# ============================================================================
# 루트 엔드포인트
# ============================================================================

@app.get("/", tags=["Info"])
async def root():
    """API 정보"""
    return {
        "name": "Memory Hub v2 API",
        "version": "0.1.0",
        "description": "Performance-Optimized Memory Management System",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "superthread": "/superthread/*",
            "google_docs": "/google-docs/*",
            "auth": "/auth/*",
        },
        "monitoring": {
            "performance_stats": "/monitoring/performance",
            "slowest_endpoints": "/monitoring/slowest",
            "most_used_endpoints": "/monitoring/most-used",
            "cache_stats": "/monitoring/cache",
        }
    }


# ============================================================================
# 성능 모니터링 엔드포인트
# ============================================================================

@app.get("/monitoring/performance", tags=["Monitoring"])
async def get_performance():
    """전체 성능 통계 조회"""
    return get_performance_stats()


@app.get("/monitoring/slowest", tags=["Monitoring"])
async def get_slowest(count: int = 5):
    """가장 느린 엔드포인트 조회"""
    return {
        "slowest_endpoints": get_slowest_endpoints(count),
        "count": count
    }


@app.get("/monitoring/most-used", tags=["Monitoring"])
async def get_most_used(count: int = 5):
    """가장 많이 사용된 엔드포인트 조회"""
    return {
        "most_used_endpoints": get_most_used_endpoints(count),
        "count": count
    }


@app.post("/monitoring/reset-performance", tags=["Monitoring"])
async def reset_perf():
    """성능 통계 리셋"""
    return reset_performance_stats()


# ============================================================================
# 캐시 관리 엔드포인트
# ============================================================================

@app.get("/monitoring/cache", tags=["Monitoring"])
async def get_cache():
    """캐시 통계 조회"""
    return get_cache_stats()


@app.post("/monitoring/cache/clear", tags=["Monitoring"])
async def clear_cache():
    """모든 캐시 비우기"""
    return clear_all_caches()


@app.post("/monitoring/cache/cleanup", tags=["Monitoring"])
async def cleanup_cache():
    """만료된 캐시 정리"""
    return cleanup_expired_caches()
