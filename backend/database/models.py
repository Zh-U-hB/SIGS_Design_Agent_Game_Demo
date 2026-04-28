# models.py — 数据库 ORM 模型定义
# 职责：定义 users、designs、likes 三张核心表的 SQLAlchemy 映射

import uuid

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class User(Base):
    """访客用户表 — 无需注册，通过 session_id 标识"""
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Design(Base):
    """设计记录表 — 存储用户创意输入、AI 设计说明、生成图片等完整设计流程数据"""
    __tablename__ = "designs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    location_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_z: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_label: Mapped[str | None] = mapped_column(String, nullable=True)
    emotion_tags: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    user_input: Mapped[str | None] = mapped_column(Text, nullable=True)
    design_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_screenshot: Mapped[str | None] = mapped_column(String, nullable=True)
    generated_images: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # 存储多张生成的图片
    selected_image: Mapped[str | None] = mapped_column(String, nullable=True)  # 用户选择的图片
    model_3d_url: Mapped[str | None] = mapped_column(String, nullable=True)
    ai_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    is_public: Mapped[bool] = mapped_column(Integer, default=0)  # 是否公开到社区
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Like(Base):
    """点赞记录表 — 同一用户对同一设计只能点赞一次"""
    __tablename__ = "likes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    design_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("designs.id"))
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "design_id"),)


class Comment(Base):
    """评论记录表 — 用户对设计的评论"""
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    design_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("designs.id"), index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
