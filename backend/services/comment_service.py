# comment_service.py — 评论业务逻辑
# 职责：处理评论的创建、获取、删除等功能

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Comment, Design
from services.session_service import get_session


async def create_comment(db: AsyncSession, design_id: str, session_id: str, content: str) -> dict:
    """创建评论"""
    user = await get_session(db, session_id)
    if not user:
        return {
            "success": False,
            "error": "Session not found"
        }

    # 检查设计是否存在
    design_result = await db.execute(
        select(Design).where(Design.id == uuid.UUID(design_id))
    )
    design = design_result.scalar_one_or_none()

    if not design:
        return {
            "success": False,
            "error": "Design not found"
        }

    # 创建评论
    comment = Comment(
        user_id=user["id"],
        design_id=uuid.UUID(design_id),
        content=content
    )
    db.add(comment)

    # 更新评论计数
    design.comments_count = (design.comments_count or 0) + 1

    await db.commit()
    await db.refresh(comment)

    return {
        "success": True,
        "id": str(comment.id),
        "content": comment.content,
        "created_at": comment.created_at.isoformat()
    }


async def get_design_comments(db: AsyncSession, design_id: str, page: int = 1, page_size: int = 50) -> dict:
    """获取设计的评论列表"""
    # 检查设计是否存在
    design_result = await db.execute(
        select(Design).where(Design.id == uuid.UUID(design_id))
    )
    design = design_result.scalar_one_or_none()

    if not design:
        return {
            "success": False,
            "error": "Design not found"
        }

    # 获取评论总数
    count_result = await db.execute(
        select(func.count()).select_from(Comment).where(Comment.design_id == uuid.UUID(design_id))
    )
    total_count = count_result.scalar() or 0

    # 获取评论列表
    offset_val = (page - 1) * page_size
    result = await db.execute(
        select(Comment)
        .where(Comment.design_id == uuid.UUID(design_id))
        .order_by(Comment.created_at.desc())
        .offset(offset_val)
        .limit(page_size)
    )
    comments = result.scalars().all()

    return {
        "success": True,
        "comments": [
            {
                "id": str(c.id),
                "user_id": str(c.user_id),
                "content": c.content,
                "created_at": c.created_at.isoformat()
            }
            for c in comments
        ],
        "total_count": total_count,
        "page": page,
        "page_size": page_size
    }


async def delete_comment(db: AsyncSession, comment_id: str, session_id: str) -> dict:
    """删除评论"""
    user = await get_session(db, session_id)
    if not user:
        return {
            "success": False,
            "error": "Session not found"
        }

    # 查找评论
    result = await db.execute(
        select(Comment).where(Comment.id == uuid.UUID(comment_id))
    )
    comment = result.scalar_one_or_none()

    if not comment:
        return {
            "success": False,
            "error": "Comment not found"
        }

    # 检查权限
    if comment.user_id != user["id"]:
        return {
            "success": False,
            "error": "Permission denied"
        }

    # 获取 design_id 用于更新计数
    design_id = comment.design_id

    # 删除评论
    await db.delete(comment)

    # 更新评论计数
    design_result = await db.execute(
        select(Design).where(Design.id == design_id)
    )
    design = design_result.scalar_one_or_none()
    if design:
        design.comments_count = max(0, (design.comments_count or 0) - 1)

    await db.commit()

    return {
        "success": True
    }
