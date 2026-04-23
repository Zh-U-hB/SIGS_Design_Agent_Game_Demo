# stats.py — 统计数据 API 端点
# 职责：返回平台参与统计数据（GET /stats）

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .deps import get_db
from schemas.common import api_success

stats_router = APIRouter()


@stats_router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
):
    """获取参与统计数据"""
    from database.models import Design, User, Like
    
    total_users = await db.execute(
        select(func.count(User.id))
    )
    total_visitors = total_users.scalar()
    
    total_designs = await db.execute(
        select(func.count(Design.id))
    )
    total_designs_count = total_designs.scalar()
    
    total_likes = await db.execute(
        select(func.count(Like.id))
    )
    total_likes_count = total_likes.scalar()
    
    result = await db.execute(
        select(Design).where(
            Design.location_x.isnot(None),
            Design.location_y.isnot(None)
        )
    )
    designs_with_location = result.scalars().all()
    locations_covered = len(set(
        (d.location_x, d.location_y) 
        for d in designs_with_location 
        if d.location_x is not None and d.location_y is not None
    ))
    
    return api_success(data={
        "total_visitors": total_visitors or 0,
        "total_designs": total_designs_count or 0,
        "total_likes": total_likes_count or 0,
        "areas_covered": locations_covered,
    })

