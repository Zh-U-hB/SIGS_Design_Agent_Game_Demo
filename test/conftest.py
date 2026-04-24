# conftest.py — 测试全局配置
# 职责：提供共享的 pytest 异步 fixtures，包括测试用 HTTP 客户端和 mock 数据库

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

# 将项目根目录加入 sys.path，使 backend 包可被正确导入
_project_root = str(Path(__file__).resolve().parent.parent)
_backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from backend.config import settings
from backend.main import app

# 确保测试环境有可用的 API Key
if not settings.API_KEY:
    settings.API_KEY = "test-api-key"


@pytest_asyncio.fixture
async def async_client():
    """创建异步 HTTP 测试客户端"""
    from httpx import ASGITransport, AsyncClient

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_db():
    """创建 mock 数据库会话"""
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.delete = AsyncMock()
    db.execute = AsyncMock()
    return db


@pytest.fixture
def override_db(mock_db):
    """覆盖 get_db 依赖为 mock 数据库，测试结束后恢复"""
    from backend.api.deps import get_db

    async def _override():
        yield mock_db

    app.dependency_overrides[get_db] = _override
    yield mock_db
    app.dependency_overrides.clear()


@pytest.fixture
def api_headers():
    """带有效 API Key 的请求头"""
    from backend.config import settings

    return {"X-API-Key": settings.API_KEY}
