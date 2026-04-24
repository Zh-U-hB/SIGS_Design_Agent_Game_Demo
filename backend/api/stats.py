# stats.py — 统计数据 API 端点
# 职责：返回平台参与统计数据（GET /stats）

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.common import api_success

from .deps import get_db

stats_router = APIRouter()


@stats_router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
):
    """获取参与统计数据"""
    from database.models import Design, Like, User

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

    areas_result = await db.execute(
        select(func.count(
            func.distinct(
                func.concat(Design.location_x, ',', Design.location_y)
            )
        )).where(
            Design.location_x.isnot(None),
            Design.location_y.isnot(None)
        )
    )
    locations_covered = areas_result.scalar() or 0

    return api_success(data={
        "total_visitors": total_visitors or 0,
        "total_designs": total_designs_count or 0,
        "total_likes": total_likes_count or 0,
        "areas_covered": locations_covered,
    })

