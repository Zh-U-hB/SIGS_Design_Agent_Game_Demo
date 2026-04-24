# test_design_service.py — 设计服务业务逻辑测试
# 职责：测试创意输入提交、设计确认、查询、列表等核心流程

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services import design_service


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.execute = AsyncMock()
    return db


def _make_design(**overrides):
    defaults = {
        "id": uuid.uuid4(),
        "user_id": uuid.uuid4(),
        "location_x": 22.595,
        "location_y": 113.935,
        "location_z": 0.0,
        "location_label": "SIGS Campus",
        "emotion_tags": ["happy", "inspired"],
        "user_input": "A beautiful garden",
        "design_description": "A modern garden design",
        "original_screenshot": "https://example.com/img.png",
        "generated_image": "https://example.com/gen.png",
        "model_3d_url": None,
        "ai_response": "AI response text",
        "likes_count": 5,
        "created_at": datetime.now(timezone.utc),
    }
    defaults.update(overrides)
    design = MagicMock()
    for k, v in defaults.items():
        setattr(design, k, v)
    return design


@pytest.mark.asyncio
async def test_submit_input_success(mock_db):
    """submit_input 应保存用户输入并返回设计数据"""
    fake_design = _make_design()

    def refresh_side_effect(obj):
        for attr in ["id", "ai_response", "location_label", "emotion_tags", "created_at"]:
            setattr(obj, attr, getattr(fake_design, attr))

    mock_db.refresh.side_effect = refresh_side_effect

    with patch.object(design_service, "get_session", return_value={"id": str(fake_design.user_id)}) as mock_get:
        from backend.schemas.design import DesignInputRequest

        request = DesignInputRequest(
            session_id="test-session",
            location_x=22.595,
            location_y=113.935,
            location_z=0.0,
            location_label="SIGS Campus",
            emotion_tags=["happy"],
            user_input="A beautiful garden",
        )
        result = await design_service.submit_input(mock_db, request)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()
    assert result["id"] == str(fake_design.id)
    assert result["ai_response"] == fake_design.ai_response


@pytest.mark.asyncio
async def test_submit_input_session_not_found(mock_db):
    """submit_input 对无效 session_id 应返回错误"""
    with patch.object(design_service, "get_session", return_value=None):
        from backend.schemas.design import DesignInputRequest

        request = DesignInputRequest(session_id="invalid-session", user_input="test")
        result = await design_service.submit_input(mock_db, request)

    assert result["error"] == "Session not found"
    assert result["id"] is None


@pytest.mark.asyncio
async def test_confirm_design_success(mock_db):
    """confirm_design 应更新记录并返回处理状态"""
    fake_design = _make_design(generated_image="生成中...")
    user_id = str(fake_design.user_id)

    scalar_result = MagicMock()
    scalar_result.scalar_one_or_none.return_value = fake_design
    mock_db.execute.return_value = scalar_result

    with patch.object(design_service, "get_session", return_value={"id": fake_design.user_id}):
        from backend.schemas.design import DesignConfirmRequest

        request = DesignConfirmRequest(
            session_id="test-session",
            design_id=str(fake_design.id),
            design_description="Updated description",
        )
        result = await design_service.confirm_design(mock_db, request)

    mock_db.commit.assert_awaited_once()
    assert result["status"] == "processing"
    assert fake_design.design_description == "Updated description"


@pytest.mark.asyncio
async def test_confirm_design_session_not_found(mock_db):
    """confirm_design 对无效 session 应返回错误"""
    with patch.object(design_service, "get_session", return_value=None):
        from backend.schemas.design import DesignConfirmRequest

        request = DesignConfirmRequest(
            session_id="invalid", design_id=str(uuid.uuid4()), design_description="test"
        )
        result = await design_service.confirm_design(mock_db, request)

    assert result["error"] == "Session not found"


@pytest.mark.asyncio
async def test_confirm_design_access_denied(mock_db):
    """confirm_design 对非本人设计应返回错误"""
    fake_design = _make_design()
    other_user_id = str(uuid.uuid4())

    scalar_result = MagicMock()
    scalar_result.scalar_one_or_none.return_value = fake_design
    mock_db.execute.return_value = scalar_result

    with patch.object(design_service, "get_session", return_value={"id": other_user_id}):
        from backend.schemas.design import DesignConfirmRequest

        request = DesignConfirmRequest(
            session_id="other-session",
            design_id=str(fake_design.id),
            design_description="hacked",
        )
        result = await design_service.confirm_design(mock_db, request)

    assert result["error"] == "Design not found or access denied"


@pytest.mark.asyncio
async def test_get_design_found(mock_db):
    """get_design 应根据 id 返回完整设计记录"""
    fake_design = _make_design()

    scalar_result = MagicMock()
    scalar_result.scalar_one_or_none.return_value = fake_design
    mock_db.execute.return_value = scalar_result

    result = await design_service.get_design(mock_db, str(fake_design.id))

    assert result is not None
    assert result["id"] == str(fake_design.id)
    assert result["user_id"] == str(fake_design.user_id)
    assert result["location_label"] == "SIGS Campus"
    assert result["likes_count"] == 5


@pytest.mark.asyncio
async def test_get_design_not_found(mock_db):
    """get_design 对不存在的 id 应返回 None"""
    scalar_result = MagicMock()
    scalar_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = scalar_result

    result = await design_service.get_design(mock_db, str(uuid.uuid4()))

    assert result is None


@pytest.mark.asyncio
async def test_get_design_status_processing(mock_db):
    """get_design_status 对生成中的设计应返回 processing"""
    fake_design = _make_design(generated_image="生成中...")

    scalar_result = MagicMock()
    scalar_result.scalar_one_or_none.return_value = fake_design
    mock_db.execute.return_value = scalar_result

    result = await design_service.get_design_status(mock_db, str(fake_design.id))

    assert result["status"] == "processing"


@pytest.mark.asyncio
async def test_get_design_status_completed(mock_db):
    """get_design_status 对已完成的设计应返回 completed"""
    fake_design = _make_design(generated_image="https://example.com/final.png")

    scalar_result = MagicMock()
    scalar_result.scalar_one_or_none.return_value = fake_design
    mock_db.execute.return_value = scalar_result

    result = await design_service.get_design_status(mock_db, str(fake_design.id))

    assert result["status"] == "completed"
    assert result["generated_image"] == "https://example.com/final.png"


@pytest.mark.asyncio
async def test_get_design_status_not_found(mock_db):
    """get_design_status 对不存在的 id 应返回 None"""
    scalar_result = MagicMock()
    scalar_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = scalar_result

    result = await design_service.get_design_status(mock_db, str(uuid.uuid4()))

    assert result is None


@pytest.mark.asyncio
async def test_list_designs(mock_db):
    """list_designs 应返回带排序的分页结果"""
    d1 = _make_design()
    d2 = _make_design()

    scalars_result = MagicMock()
    scalars_result.all.return_value = [d1, d2]
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value = scalars_result
    mock_db.execute.return_value = mock_execute_result

    from backend.schemas.design import DesignListParams

    params = DesignListParams(page=1, page_size=10, sort_by="created_at", order="desc")
    result = await design_service.list_designs(mock_db, params)

    assert len(result["designs"]) == 2
    assert result["page"] == 1
    assert result["page_size"] == 10


@pytest.mark.asyncio
async def test_get_map_points(mock_db):
    """get_map_points 应返回所有带位置的设计光点"""
    d1 = _make_design()
    d2 = _make_design(location_x=None, location_y=None)

    scalars_result = MagicMock()
    scalars_result.all.return_value = [d1, d2]
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value = scalars_result
    mock_db.execute.return_value = mock_execute_result

    result = await design_service.get_map_points(mock_db)

    assert len(result) == 1
    assert result[0]["location_x"] == d1.location_x
