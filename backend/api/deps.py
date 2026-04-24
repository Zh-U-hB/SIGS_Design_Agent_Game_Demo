# deps.py — API 依赖注入
# 职责：提供数据库会话、API Key 验证、当前会话获取等共享依赖

import hmac
from collections.abc import AsyncGenerator

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.database.connection import get_db_session
from backend.schemas.common import AUTH_ERROR, NOT_FOUND, api_error


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（用于依赖注入）"""
    async for session in get_db_session():
        yield session


async def verify_api_key(x_api_key: str = Header(...)) -> str:
    """验证请求头中的 API Key"""
    if not hmac.compare_digest(x_api_key, settings.API_KEY):
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail=api_error(AUTH_ERROR, "API Key 缺失或无效"))
    return x_api_key


async def get_current_session(session_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    """通过 session_id 获取当前用户，不存在则返回 404"""
    from backend.services import session_service

    user = await session_service.get_session(db, session_id)
    if not user:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail=api_error(NOT_FOUND, "会话不存在"))
    return user
