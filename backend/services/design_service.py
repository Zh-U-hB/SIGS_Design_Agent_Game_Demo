# design_service.py — 设计流程业务逻辑
# 职责：处理创意输入提交、设计确认、状态查询、列表获取、地图数据等核心设计流程

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Design
from schemas.design import DesignConfirmRequest, DesignInputRequest, DesignListParams

from .agent_service import translate_to_design_spec
from .image_service import generate_image
from .model3d_service import convert_to_3d
from .session_service import get_session


async def submit_input(db: AsyncSession, request: DesignInputRequest) -> dict:
    """保存用户创意输入并触发 Agent 处理"""
    user = await get_session(db, request.session_id)
    if not user:
        return {
            "id": None,
            "ai_response": None,
            "error": "Session not found"
        }

    agent_result = await translate_to_design_spec(
        emotion_tags=request.emotion_tags,
        user_input=request.user_input,
        location_label=request.location_label
    )

    design = Design(
        user_id=user["id"],
        location_x=request.location_x,
        location_y=request.location_y,
        location_z=request.location_z,
        location_label=request.location_label,
        emotion_tags=request.emotion_tags,
        user_input=request.user_input,
        original_screenshot=request.original_screenshot,
        ai_response=agent_result["ai_response"],
        design_description=agent_result["design_description"]
    )
    db.add(design)
    await db.commit()
    await db.refresh(design)

    return {
        "id": str(design.id),
        "ai_response": design.ai_response,
        "location_label": design.location_label,
        "emotion_tags": design.emotion_tags,
        "created_at": design.created_at.isoformat()
    }


async def confirm_design(db: AsyncSession, request: DesignConfirmRequest) -> dict:
    """确认设计说明并触发图生图生成"""
    user = await get_session(db, request.session_id)
    if not user:
        return {
            "error": "Session not found"
        }

    result = await db.execute(
        select(Design).where(Design.id == uuid.UUID(request.design_id))
    )
    design = result.scalar_one_or_none()

    if not design or design.user_id != user["id"]:
        return {
            "error": "Design not found or access denied"
        }

    design.design_description = request.design_description

    image_result = await generate_image(
        design_id=str(design.id),
        design_description=design.design_description,
        original_screenshot=design.original_screenshot
    )

    if image_result["success"]:
        design.generated_image = image_result.get("image_url", "生成中...")
        # 发起 3D 转换并存储 task_id
        conversion_result = await convert_to_3d(
            image_url=design.generated_image,
            design_id=str(design.id)
        )
        if conversion_result["success"]:
            design.model_3d_url = conversion_result.get("model_url", "生成中...")
        else:
            design.model_3d_url = None
        status = "processing"
    else:
        design.generated_image = "图片生成失败"
        design.model_3d_url = None
        status = "failed"

    await db.commit()
    await db.refresh(design)

    return {
        "id": str(design.id),
        "design_description": design.design_description,
        "generated_image": design.generated_image,
        "model_3d_url": design.model_3d_url,
        "status": status
    }


async def get_design(db: AsyncSession, design_id: str) -> dict | None:
    """根据 id 获取设计完整详情"""
    result = await db.execute(
        select(Design).where(Design.id == uuid.UUID(design_id))
    )
    design = result.scalar_one_or_none()

    if not design:
        return None

    return {
        "id": str(design.id),
        "user_id": str(design.user_id),
        "location_x": design.location_x,
        "location_y": design.location_y,
        "location_z": design.location_z,
        "location_label": design.location_label,
        "emotion_tags": design.emotion_tags,
        "user_input": design.user_input,
        "design_description": design.design_description,
        "original_screenshot": design.original_screenshot,
        "generated_image": design.generated_image,
        "model_3d_url": design.model_3d_url,
        "ai_response": design.ai_response,
        "likes_count": design.likes_count,
        "created_at": design.created_at.isoformat()
    }


async def get_design_status(db: AsyncSession, design_id: str) -> dict | None:
    """查询异步生成状态（图生图、3D模型），只读不触发副作用"""
    result = await db.execute(
        select(Design).where(Design.id == uuid.UUID(design_id))
    )
    design = result.scalar_one_or_none()

    if not design:
        return None

    image_done = bool(design.generated_image and design.generated_image not in ("生成中...", "图片生成失败"))
    model_done = bool(design.model_3d_url and design.model_3d_url not in ("生成中...", "3D转换失败"))

    if image_done and model_done:
        status = "completed"
    elif design.generated_image == "图片生成失败":
        status = "failed"
    else:
        status = "processing"

    return {
        "id": str(design.id),
        "status": status,
        "generated_image": design.generated_image,
        "model_3d_url": design.model_3d_url,
        "design_description": design.design_description
    }


async def list_designs(db: AsyncSession, params: DesignListParams) -> dict:
    """获取设计列表，支持分页和排序"""
    query = select(Design)

    order_column = Design.created_at
    if params.sort_by == "likes_count":
        order_column = Design.likes_count
    else:
        order_column = Design.created_at

    if params.order == "desc":
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column.asc())

    offset_val = (params.page - 1) * params.page_size

    count_result = await db.execute(select(func.count()).select_from(Design))
    total_count = count_result.scalar() or 0

    result = await db.execute(
        query.offset(offset_val).limit(params.page_size)
    )
    designs = result.scalars().all()

    return {
        "designs": [
            {
                "id": str(d.id),
                "user_id": str(d.user_id),
                "location_x": d.location_x,
                "location_y": d.location_y,
                "location_z": d.location_z,
                "location_label": d.location_label,
                "emotion_tags": d.emotion_tags,
                "design_description": d.design_description,
                "generated_image": d.generated_image,
                "model_3d_url": d.model_3d_url,
                "likes_count": d.likes_count,
                "created_at": d.created_at.isoformat()
            }
            for d in designs
        ],
        "page": params.page,
        "page_size": params.page_size,
        "total_count": total_count
    }


async def get_map_points(db: AsyncSession) -> list[dict]:
    """获取所有设计的地图光点数据（用于社区 Gallery 页面的校园地图可视化）"""
    result = await db.execute(
        select(Design).where(Design.location_x.isnot(None), Design.location_y.isnot(None))
    )
    designs = result.scalars().all()

    return [
        {
            "id": str(d.id),
            "location_x": d.location_x,
            "location_y": d.location_y,
            "location_z": d.location_z,
            "location_label": d.location_label,
            "likes_count": d.likes_count
        }
        for d in designs
        if d.location_x is not None and d.location_y is not None
    ]

