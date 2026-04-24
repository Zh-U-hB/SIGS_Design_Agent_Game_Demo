# serve.py — 数据库服务工具函数
# 职责：提供建表、删表、连通性检查等开发辅助函数

from sqlalchemy import text

from backend.database.connection import _get_engine
from backend.database.models import Base
from backend.utils.logger import get_logger

logger = get_logger(__name__)


async def create_tables() -> None:
    """创建所有数据表（仅开发环境使用，生产环境请使用迁移脚本）"""
    engine = _get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("所有数据表创建完成。")


async def drop_tables() -> None:
    """删除所有数据表（仅开发环境使用，危险操作！）"""
    logger.warning("正在删除所有数据表！")
    engine = _get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.info("所有数据表已删除。")


async def check_connection() -> bool:
    """验证数据库连通性"""
    try:
        engine = _get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error("数据库连接失败: %s", e)
        return False
