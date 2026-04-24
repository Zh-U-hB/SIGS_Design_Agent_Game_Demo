# test_session_service.py — 会话服务业务逻辑测试
# 职责：测试会话创建和查询逻辑

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services import session_service


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.execute = AsyncMock()
    return db


def _make_user(session_id):
    user = MagicMock()
    user.id = uuid.uuid4()
    user.session_id = session_id
    user.created_at = datetime.now(timezone.utc)
    return user


@pytest.mark.asyncio
async def test_create_session(mock_db):
    """create_session 应生成 UUID session_id 并插入 users 表"""
    fake_user = _make_user("test-session-id")

    def refresh_side_effect(obj):
        obj.id = fake_user.id
        obj.session_id = fake_user.session_id
        obj.created_at = fake_user.created_at

    mock_db.refresh.side_effect = refresh_side_effect

    result = await session_service.create_session(mock_db)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once()
    assert result["session_id"] == fake_user.session_id
    assert "id" in result
    assert "created_at" in result


@pytest.mark.asyncio
async def test_get_session_found(mock_db):
    """get_session 对有效的 session_id 应返回用户数据"""
    fake_user = _make_user("existing-session-id")
    scalar_result = MagicMock()
    scalar_result.scalar_one_or_none.return_value = fake_user
    mock_db.execute.return_value = scalar_result

    result = await session_service.get_session(mock_db, "existing-session-id")

    assert result is not None
    assert result["session_id"] == "existing-session-id"
    assert "id" in result
    assert "created_at" in result


@pytest.mark.asyncio
async def test_get_session_not_found(mock_db):
    """get_session 对不存在的 session_id 应返回 None"""
    scalar_result = MagicMock()
    scalar_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = scalar_result

    result = await session_service.get_session(mock_db, "nonexistent-id")

    assert result is None
