# connection.py — 异步数据库连接管理
# 职责：创建 SQLAlchemy 异步引擎和会话工厂，提供懒初始化和依赖注入用的 get_db_session

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.config import settings

_engine = None
_async_session_factory = None


def _get_engine():
    """懒初始化异步引擎和会话工厂，避免无数据库配置时启动报错"""
    global _engine, _async_session_factory
    if _engine is None:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE,
        )
        _async_session_factory = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    return _engine


def _get_session_factory():
    """获取会话工厂，确保引擎已初始化"""
    if _async_session_factory is None:
        _get_engine()
    return _async_session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖注入：生成数据库会话"""
    factory = _get_session_factory()
    async with factory() as session:
        yield session


async def init_db() -> None:
    """启动时验证数据库连通性"""
    eng = _get_engine()
    async with eng.begin() as conn:
        await conn.execute(text("SELECT 1"))


async def close_db() -> None:
    """关闭时释放引擎资源"""
    if _engine is not None:
        await _engine.dispose()
