# session.py — 会话相关请求/响应模型
# 职责：定义创建会话、会话响应的 Pydantic 数据模型

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SessionCreateRequest(BaseModel):
    """创建会话请求（无需参数，系统自动生成）"""
    pass


class SessionResponse(BaseModel):
    """会话响应数据"""
    id: UUID
    session_id: str
    created_at: datetime
