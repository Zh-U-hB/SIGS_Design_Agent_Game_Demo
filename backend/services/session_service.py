# session_service.py — 会话管理业务逻辑
# 职责：处理访客会话的创建和查询

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import User


async def create_session(db: AsyncSession) -> dict:
    """创建新的访客会话，返回包含 session_id 的会话数据"""
    session_id = str(uuid.uuid4())
    user = User(session_id=session_id)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {
        "id": str(user.id),
        "session_id": user.session_id,
        "created_at": user.created_at.isoformat()
    }


async def get_session(db: AsyncSession, session_id: str) -> dict | None:
    """通过 session_id 查询用户，返回用户数据或 None"""
    result = await db.execute(
        select(User).where(User.session_id == session_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        return None
    return {
        "id": str(user.id),
        "session_id": user.session_id,
        "created_at": user.created_at.isoformat()
    }

