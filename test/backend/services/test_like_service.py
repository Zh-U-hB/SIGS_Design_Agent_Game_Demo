# test_like_service.py — 点赞服务业务逻辑测试
# 职责：测试点赞和取消点赞逻辑

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.services import like_service


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.delete = AsyncMock()
    db.execute = AsyncMock()
    return db


def _make_design(design_id=None, likes_count=0):
    design = MagicMock()
    design.id = design_id or uuid.uuid4()
    design.likes_count = likes_count
    return design


def _make_like(user_id, design_id):
    like = MagicMock()
    like.user_id = user_id
    like.design_id = design_id
    return like


@pytest.mark.asyncio
async def test_like_design_success(mock_db):
    """like_design 应添加点赞记录并递增计数"""
    user_id = str(uuid.uuid4())
    design_id = str(uuid.uuid4())
    fake_design = _make_design(uuid.UUID(design_id), likes_count=3)

    results = []

    def execute_side_effect(stmt):
        result = MagicMock()
        idx = len(results)
        results.append(idx)
        if idx == 0:
            result.scalar_one_or_none.return_value = None
        else:
            result.scalar_one_or_none.return_value = fake_design
        return result

    mock_db.execute.side_effect = execute_side_effect

    result = await like_service.like_design(mock_db, user_id, design_id)

    assert result["success"] is True
    assert result["message"] == "Liked successfully"
    assert fake_design.likes_count == 4
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_like_design_already_liked(mock_db):
    """like_design 对已点赞的设计应返回失败"""
    user_id = str(uuid.uuid4())
    design_id = str(uuid.uuid4())
    existing_like = _make_like(user_id, design_id)

    scalar_result = MagicMock()
    scalar_result.scalar_one_or_none.return_value = existing_like
    mock_db.execute.return_value = scalar_result

    result = await like_service.like_design(mock_db, user_id, design_id)

    assert result["success"] is False
    assert result["message"] == "Already liked"


@pytest.mark.asyncio
async def test_unlike_design_success(mock_db):
    """unlike_design 应删除点赞记录并递减计数"""
    user_id = str(uuid.uuid4())
    design_id = str(uuid.uuid4())
    existing_like = _make_like(user_id, design_id)
    fake_design = _make_design(uuid.UUID(design_id), likes_count=5)

    results = []

    def execute_side_effect(stmt):
        result = MagicMock()
        idx = len(results)
        results.append(idx)
        if idx == 0:
            result.scalar_one_or_none.return_value = existing_like
        else:
            result.scalar_one_or_none.return_value = fake_design
        return result

    mock_db.execute.side_effect = execute_side_effect

    result = await like_service.unlike_design(mock_db, user_id, design_id)

    assert result["success"] is True
    assert result["message"] == "Unliked successfully"
    assert fake_design.likes_count == 4
    mock_db.delete.assert_awaited_once()
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_unlike_design_not_liked(mock_db):
    """unlike_design 对未点赞的设计应返回失败"""
    user_id = str(uuid.uuid4())
    design_id = str(uuid.uuid4())

    scalar_result = MagicMock()
    scalar_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = scalar_result

    result = await like_service.unlike_design(mock_db, user_id, design_id)

    assert result["success"] is False
    assert result["message"] == "Not liked yet"


@pytest.mark.asyncio
async def test_unlike_design_count_floor(mock_db):
    """unlike_design 不应让 likes_count 降到负数"""
    user_id = str(uuid.uuid4())
    design_id = str(uuid.uuid4())
    existing_like = _make_like(user_id, design_id)
    fake_design = _make_design(uuid.UUID(design_id), likes_count=0)

    results = []

    def execute_side_effect(stmt):
        result = MagicMock()
        idx = len(results)
        results.append(idx)
        if idx == 0:
            result.scalar_one_or_none.return_value = existing_like
        else:
            result.scalar_one_or_none.return_value = fake_design
        return result

    mock_db.execute.side_effect = execute_side_effect

    result = await like_service.unlike_design(mock_db, user_id, design_id)

    assert result["success"] is True
    assert fake_design.likes_count == 0
