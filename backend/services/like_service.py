# like_service.py — 点赞业务逻辑
# 职责：处理设计点赞和取消点赞操作

import uuid

from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import Design, Like


async def like_design(db: AsyncSession, user_id: str, design_id: str) -> dict:
    """用户点赞设计"""
    result = await db.execute(
        select(Like).where(
            Like.user_id == user_id,
            Like.design_id == design_id
        )
    )
    existing_like = result.scalar_one_or_none()

    if existing_like:
        return {
            "success": False,
            "message": "Already liked"
        }

    like = Like(user_id=user_id, design_id=design_id)
    db.add(like)

    await db.execute(
        update(Design)
        .where(Design.id == uuid.UUID(design_id))
        .values(likes_count=Design.likes_count + 1)
    )

    await db.commit()

    return {
        "success": True,
        "message": "Liked successfully"
    }


async def unlike_design(db: AsyncSession, user_id: str, design_id: str) -> dict:
    """用户取消点赞"""
    result = await db.execute(
        select(Like).where(
            Like.user_id == user_id,
            Like.design_id == design_id
        )
    )
    existing_like = result.scalar_one_or_none()

    if not existing_like:
        return {
            "success": False,
            "message": "Not liked yet"
        }

    await db.delete(existing_like)

    await db.execute(
        text("UPDATE designs SET likes_count = GREATEST(likes_count - 1, 0) WHERE id = :id"),
        {"id": uuid.UUID(design_id)}
    )

    await db.commit()

    return {
        "success": True,
        "message": "Unliked successfully"
    }
