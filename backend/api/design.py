# design.py — 设计流程 API 端点
# 职责：处理创意输入、设计确认、状态查询、列表获取、地图光点、点赞等 8 个端点

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db
from backend.schemas.common import api_success
from backend.schemas.design import DesignConfirmRequest, DesignInputRequest, DesignListParams
from backend.services import design_service, like_service

design_router = APIRouter()


@design_router.post("/designs/input")
async def submit_creative_input(
    request: DesignInputRequest,
    db: AsyncSession = Depends(get_db),
):
    """提交创意输入 → Agent 处理"""
    result = await design_service.submit_input(db, request)
    return api_success(data=result)


@design_router.post("/designs/{design_id}/confirm")
async def confirm_design(
    design_id: str,
    request: DesignConfirmRequest,
    db: AsyncSession = Depends(get_db),
):
    """确认设计说明 → 触发图生图"""
    request.design_id = design_id
    result = await design_service.confirm_design(db, request)
    return api_success(data=result)


@design_router.get("/designs")
async def list_designs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    order: str = Query("desc"),
    db: AsyncSession = Depends(get_db),
):
    """获取设计列表（支持分页、排序）"""
    params = DesignListParams(page=page, page_size=page_size, sort_by=sort_by, order=order)
    result = await design_service.list_designs(db, params)
    return api_success(data=result)


@design_router.get("/designs/map")
async def get_map_points(
    db: AsyncSession = Depends(get_db),
):
    """获取地图光点数据"""
    result = await design_service.get_map_points(db)
    return api_success(data=result)


@design_router.get("/designs/{design_id}")
async def get_design(
    design_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取设计详情"""
    result = await design_service.get_design(db, design_id)
    return api_success(data=result)


@design_router.get("/designs/{design_id}/status")
async def get_design_status(
    design_id: str,
    db: AsyncSession = Depends(get_db),
):
    """查询生成状态（轮询）"""
    result = await design_service.get_design_status(db, design_id)
    return api_success(data=result)


@design_router.post("/designs/{design_id}/like")
async def like_design(
    design_id: str,
    session_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """点赞"""
    from backend.services import session_service

    user = await session_service.get_session(db, session_id)
    if not user:
        return api_success(data={"success": False, "message": "会话不存在"}, code=40401)
    result = await like_service.like_design(db, str(user["id"]), design_id)
    return api_success(data=result)


@design_router.delete("/designs/{design_id}/like")
async def unlike_design(
    design_id: str,
    session_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """取消点赞"""
    from backend.services import session_service

    user = await session_service.get_session(db, session_id)
    if not user:
        return api_success(data={"success": False, "message": "会话不存在"}, code=40401)
    result = await like_service.unlike_design(db, str(user["id"]), design_id)
    return api_success(data=result)
