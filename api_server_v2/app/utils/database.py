"""
데이터베이스 연결 풀링 유틸리티

SQLAlchemy 기반 데이터베이스 연결 풀링 설정:
- 커넥션 풀 관리
- 풀 재활용 및 유효성 검사
- 비동기 쿼리 지원
"""

from typing import Optional, Dict, Any
from sqlalchemy import create_engine, pool, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool, NullPool, StaticPool
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# 데이터베이스 엔진 팩토리
# ============================================================================

class DatabaseEngineFactory:
    """데이터베이스 엔진 생성 및 관리"""

    _engines: Dict[str, Any] = {}

    @staticmethod
    def create_engine(
        database_url: str,
        engine_type: str = "async",
        pool_size: int = 20,
        max_overflow: int = 40,
        pool_recycle: int = 3600,
        echo: bool = False,
        **kwargs
    ) -> Any:
        """
        데이터베이스 엔진 생성

        Args:
            database_url: 데이터베이스 연결 URL
            engine_type: 엔진 타입 ("async" 또는 "sync")
            pool_size: 커넥션 풀 기본 크기
            max_overflow: 최대 오버플로우 커넥션 수
            pool_recycle: 커넥션 재활용 시간 (초)
            echo: SQL 쿼리 로깅 여부
            **kwargs: 추가 엔진 옵션

        Returns:
            생성된 엔진

        Examples:
            # 비동기 엔진
            engine = DatabaseEngineFactory.create_engine(
                "sqlite+aiosqlite:///:memory:",
                engine_type="async"
            )

            # 동기 엔진
            engine = DatabaseEngineFactory.create_engine(
                "sqlite:///memory.db",
                engine_type="sync"
            )
        """
        if database_url in DatabaseEngineFactory._engines:
            return DatabaseEngineFactory._engines[database_url]

        if engine_type == "async":
            engine = create_async_engine(
                database_url,
                echo=echo,
                poolclass=QueuePool,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_pre_ping=True,  # 커넥션 유효성 검사
                pool_recycle=pool_recycle,
                **kwargs
            )
        else:  # sync
            engine = create_engine(
                database_url,
                echo=echo,
                poolclass=QueuePool,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_pre_ping=True,  # 커넥션 유효성 검사
                pool_recycle=pool_recycle,
                **kwargs
            )

        DatabaseEngineFactory._engines[database_url] = engine
        logger.info(
            f"✅ 데이터베이스 엔진 생성: {engine_type} "
            f"(pool_size={pool_size}, max_overflow={max_overflow})"
        )
        return engine

    @staticmethod
    def get_engine(database_url: str) -> Optional[Any]:
        """기존 엔진 조회"""
        return DatabaseEngineFactory._engines.get(database_url)

    @staticmethod
    def dispose_engine(database_url: str) -> None:
        """엔진 리소스 해제"""
        if database_url in DatabaseEngineFactory._engines:
            engine = DatabaseEngineFactory._engines[database_url]
            if hasattr(engine, 'dispose'):
                engine.dispose()
            elif hasattr(engine, 'sync_engine'):
                engine.sync_engine.dispose()
            del DatabaseEngineFactory._engines[database_url]
            logger.info(f"✅ 데이터베이스 엔진 해제: {database_url}")

    @staticmethod
    def dispose_all() -> None:
        """모든 엔진 리소스 해제"""
        for database_url in list(DatabaseEngineFactory._engines.keys()):
            DatabaseEngineFactory.dispose_engine(database_url)


# ============================================================================
# 세션 팩토리
# ============================================================================

class SessionFactory:
    """데이터베이스 세션 생성 및 관리"""

    _session_makers: Dict[str, Any] = {}

    @staticmethod
    def create_session_maker(
        database_url: str,
        engine_type: str = "async",
        **engine_kwargs
    ) -> Any:
        """
        세션 메이커 생성

        Args:
            database_url: 데이터베이스 연결 URL
            engine_type: 엔진 타입
            **engine_kwargs: 엔진 생성 옵션

        Returns:
            세션 메이커

        Examples:
            SessionMaker = SessionFactory.create_session_maker(
                "sqlite+aiosqlite:///:memory:"
            )
            async with SessionMaker() as session:
                result = await session.execute(query)
        """
        if database_url in SessionFactory._session_makers:
            return SessionFactory._session_makers[database_url]

        engine = DatabaseEngineFactory.create_engine(
            database_url,
            engine_type=engine_type,
            **engine_kwargs
        )

        if engine_type == "async":
            session_maker = async_sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
        else:
            from sqlalchemy.orm import sessionmaker
            session_maker = sessionmaker(
                bind=engine,
                expire_on_commit=False
            )

        SessionFactory._session_makers[database_url] = session_maker
        logger.info(f"✅ 세션 메이커 생성: {database_url}")
        return session_maker

    @staticmethod
    def get_session_maker(database_url: str) -> Optional[Any]:
        """기존 세션 메이커 조회"""
        return SessionFactory._session_makers.get(database_url)

    @staticmethod
    def close_session_maker(database_url: str) -> None:
        """세션 메이커 종료"""
        if database_url in SessionFactory._session_makers:
            del SessionFactory._session_makers[database_url]
            DatabaseEngineFactory.dispose_engine(database_url)
            logger.info(f"✅ 세션 메이커 종료: {database_url}")

    @staticmethod
    def close_all_session_makers() -> None:
        """모든 세션 메이커 종료"""
        for database_url in list(SessionFactory._session_makers.keys()):
            SessionFactory.close_session_maker(database_url)


# ============================================================================
# 풀 모니터링
# ============================================================================

class PoolMonitor:
    """커넥션 풀 상태 모니터링"""

    @staticmethod
    def get_pool_stats(engine) -> dict:
        """
        풀 통계 조회

        Args:
            engine: SQLAlchemy 엔진

        Returns:
            풀 통계 딕셔너리
        """
        try:
            if hasattr(engine, 'pool'):
                pool = engine.pool
            elif hasattr(engine, 'sync_engine'):
                pool = engine.sync_engine.pool
            else:
                return {"status": "pool not available"}

            if isinstance(pool, QueuePool):
                return {
                    "type": "QueuePool",
                    "size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow(),
                    "queue_size": pool.queue.qsize() if hasattr(pool, 'queue') else "N/A"
                }
            elif isinstance(pool, NullPool):
                return {"type": "NullPool", "status": "No pooling"}
            elif isinstance(pool, StaticPool):
                return {"type": "StaticPool", "status": "Static pooling"}
            else:
                return {"type": str(type(pool)), "status": "Unknown pool type"}
        except Exception as e:
            logger.error(f"풀 통계 조회 실패: {str(e)}")
            return {"status": "error", "error": str(e)}

    @staticmethod
    def print_pool_stats(engine, label: str = "") -> None:
        """풀 통계 출력"""
        stats = PoolMonitor.get_pool_stats(engine)
        print(f"\n📊 커넥션 풀 상태 {label}:")
        for key, value in stats.items():
            print(f"  {key}: {value}")


# ============================================================================
# 설정 프리셋
# ============================================================================

# 개발 환경 설정
DEV_POOL_CONFIG = {
    "pool_size": 5,
    "max_overflow": 10,
    "pool_recycle": 3600,
}

# 프로덕션 환경 설정
PROD_POOL_CONFIG = {
    "pool_size": 20,
    "max_overflow": 40,
    "pool_recycle": 3600,
}

# 테스트 환경 설정
TEST_POOL_CONFIG = {
    "pool_size": 2,
    "max_overflow": 0,
    "pool_recycle": 3600,
}


# ============================================================================
# 헬퍼 함수
# ============================================================================

def get_pool_config(environment: str = "dev") -> dict:
    """환경별 풀 설정 조회"""
    configs = {
        "dev": DEV_POOL_CONFIG,
        "prod": PROD_POOL_CONFIG,
        "test": TEST_POOL_CONFIG,
    }
    return configs.get(environment, DEV_POOL_CONFIG)


def create_database_engine(
    database_url: str,
    environment: str = "dev",
    **kwargs
):
    """
    환경별 데이터베이스 엔진 생성

    Args:
        database_url: 데이터베이스 URL
        environment: 환경 ("dev", "prod", "test")
        **kwargs: 추가 설정

    Returns:
        생성된 엔진
    """
    pool_config = get_pool_config(environment)
    pool_config.update(kwargs)
    return DatabaseEngineFactory.create_engine(database_url, **pool_config)


def get_database_session_maker(
    database_url: str,
    environment: str = "dev",
    **kwargs
):
    """
    환경별 세션 메이커 생성

    Args:
        database_url: 데이터베이스 URL
        environment: 환경
        **kwargs: 추가 설정

    Returns:
        세션 메이커
    """
    pool_config = get_pool_config(environment)
    pool_config.update(kwargs)
    return SessionFactory.create_session_maker(database_url, **pool_config)
