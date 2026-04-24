# design.py — 设计流程相关请求/响应模型
# 职责：定义创意输入、设计确认、设计详情、地图光点等 Pydantic 数据模型

from datetime import datetime

from pydantic import BaseModel, Field


class DesignInputRequest(BaseModel):
    """创意输入请求 — 包含位置信息、情绪标签和用户自由描述"""
    session_id: str = Field(max_length=64)
    location_x: float | None = None
    location_y: float | None = None
    location_z: float | None = None
    location_label: str | None = Field(default=None, max_length=100)
    emotion_tags: list[str] | None = None
    user_input: str = Field(max_length=2000)
    original_screenshot: str | None = None


class DesignConfirmRequest(BaseModel):
    """设计确认请求 — 用户确认或编辑后的设计说明"""
    session_id: str = Field(max_length=64)
    design_id: str = ""
    design_description: str = Field(max_length=2000)


class DesignResponse(BaseModel):
    """设计详情响应 — 包含完整的设计记录数据"""
    id: str
    user_id: str
    location_x: float | None
    location_y: float | None
    location_z: float | None
    location_label: str | None
    emotion_tags: list[str] | None
    user_input: str | None
    design_description: str | None
    original_screenshot: str | None
    generated_image: str | None
    model_3d_url: str | None
    ai_response: str | None
    likes_count: int
    created_at: datetime


class DesignStatusResponse(BaseModel):
    """设计生成状态响应 — 用于轮询图生图和3D模型生成进度"""
    design_id: str
    status: str  # "processing"（处理中）| "completed"（已完成）| "failed"（失败）
    generated_image: str | None = None
    model_3d_url: str | None = None


class DesignMapPoint(BaseModel):
    """地图光点数据 — 用于社区 Gallery 页面的校园地图可视化"""
    id: str
    location_x: float
    location_y: float
    location_z: float
    location_label: str | None
    likes_count: int


class DesignListParams(BaseModel):
    """设计列表查询参数 — 支持分页和排序"""
    page: int = 1
    page_size: int = 20
    sort_by: str = "created_at"  # "created_at"（按时间）| "likes_count"（按点赞数）
    order: str = "desc"  # "desc"（降序）| "asc"（升序）
