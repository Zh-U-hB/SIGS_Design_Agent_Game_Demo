# test_design.py — 设计流程 API 端点测试
# 职责：测试创意输入、设计确认、状态查询、列表、地图光点、点赞等 8 个端点

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _make_design(**overrides):
    defaults = {
        "id": uuid.uuid4(),
        "user_id": uuid.uuid4(),
        "location_x": 22.595,
        "location_y": 113.935,
        "location_z": 0.0,
        "location_label": "SIGS Campus",
        "emotion_tags": ["happy"],
        "user_input": "A garden",
        "design_description": "A modern garden",
        "original_screenshot": None,
        "generated_image": "https://example.com/gen.png",
        "model_3d_url": None,
        "ai_response": "AI response",
        "likes_count": 3,
        "created_at": datetime.now(timezone.utc),
    }
    defaults.update(overrides)
    d = MagicMock()
    for k, v in defaults.items():
        setattr(d, k, v)
    return d


@pytest.mark.asyncio
async def test_submit_creative_input(async_client, override_db, api_headers):
    """POST /api/v1/designs/input 应接受情绪标签和用户文字"""
    fake_design = _make_design()

    def refresh_side_effect(obj):
        obj.id = fake_design.id
        obj.ai_response = fake_design.ai_response
        obj.location_label = fake_design.location_label
        obj.emotion_tags = fake_design.emotion_tags
        obj.created_at = fake_design.created_at

    override_db.refresh.side_effect = refresh_side_effect

    with patch("backend.services.design_service.get_session", return_value={"id": str(fake_design.user_id)}):
        response = await async_client.post(
            "/api/v1/designs/input",
            json={
                "session_id": "test-session",
                "location_x": 22.595,
                "location_y": 113.935,
                "user_input": "A beautiful garden",
                "emotion_tags": ["happy", "inspired"],
            },
            headers=api_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["id"] == str(fake_design.id)


@pytest.mark.asyncio
async def test_confirm_design(async_client, override_db, api_headers):
    """POST /api/v1/designs/confirm 应更新设计并触发图生图"""
    fake_design = _make_design(generated_image="生成中...")

    scalar_result = MagicMock()
    scalar_result.scalar_one_or_none.return_value = fake_design
    override_db.execute.return_value = scalar_result

    with patch("backend.services.design_service.get_session", return_value={"id": fake_design.user_id}):
        response = await async_client.post(
            "/api/v1/designs/confirm",
            json={
                "session_id": "test-session",
                "design_id": str(fake_design.id),
                "design_description": "Updated description",
            },
            headers=api_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["status"] == "processing"


@pytest.mark.asyncio
async def test_get_design(async_client, override_db, api_headers):
    """GET /api/v1/designs/{id} 应返回完整设计详情"""
    fake_design = _make_design()

    scalar_result = MagicMock()
    scalar_result.scalar_one_or_none.return_value = fake_design
    override_db.execute.return_value = scalar_result

    response = await async_client.get(
        f"/api/v1/designs/{fake_design.id}",
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["id"] == str(fake_design.id)


@pytest.mark.asyncio
async def test_get_design_status(async_client, override_db, api_headers):
    """GET /api/v1/designs/{id}/status 应返回生成状态"""
    fake_design = _make_design(generated_image="生成中...")

    scalar_result = MagicMock()
    scalar_result.scalar_one_or_none.return_value = fake_design
    override_db.execute.return_value = scalar_result

    response = await async_client.get(
        f"/api/v1/designs/{fake_design.id}/status",
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["status"] == "processing"


@pytest.mark.asyncio
async def test_list_designs(async_client, override_db, api_headers):
    """GET /api/v1/designs 应返回分页设计列表"""
    d1 = _make_design()
    d2 = _make_design()

    scalars_result = MagicMock()
    scalars_result.all.return_value = [d1, d2]
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value = scalars_result
    override_db.execute.return_value = mock_execute_result

    response = await async_client.get(
        "/api/v1/designs?page=1&page_size=10",
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert len(data["data"]["designs"]) == 2


@pytest.mark.asyncio
async def test_get_map_points(async_client, override_db, api_headers):
    """GET /api/v1/designs/map 应返回位置光点数据"""
    d1 = _make_design()

    scalars_result = MagicMock()
    scalars_result.all.return_value = [d1]
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value = scalars_result
    override_db.execute.return_value = mock_execute_result

    response = await async_client.get(
        "/api/v1/designs/map",
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert len(data["data"]) >= 1


@pytest.mark.asyncio
async def test_like_design(async_client, override_db, api_headers):
    """POST /api/v1/designs/{id}/like 应递增点赞数"""
    design_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    fake_design = _make_design(id=uuid.UUID(design_id), likes_count=3)

    results = []

    def execute_side_effect(stmt):
        result = MagicMock()
        idx = len(results)
        results.append(idx)
        if idx == 0:
            result.scalar_one_or_none.return_value = None
        elif idx == 1:
            result.scalar_one_or_none.return_value = fake_design
        else:
            result.scalar_one_or_none.return_value = None
        return result

    override_db.execute.side_effect = execute_side_effect

    with patch("backend.services.session_service.get_session", return_value={"id": user_id, "session_id": "test"}):
        response = await async_client.post(
            f"/api/v1/designs/{design_id}/like?session_id=test",
            headers=api_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["success"] is True


@pytest.mark.asyncio
async def test_unlike_design(async_client, override_db, api_headers):
    """DELETE /api/v1/designs/{id}/like 应递减点赞数"""
    design_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    fake_design = _make_design(id=uuid.UUID(design_id), likes_count=5)
    existing_like = MagicMock()

    results = []

    def execute_side_effect(stmt):
        result = MagicMock()
        idx = len(results)
        results.append(idx)
        if idx == 0:
            result.scalar_one_or_none.return_value = existing_like
        elif idx == 1:
            result.scalar_one_or_none.return_value = fake_design
        else:
            result.scalar_one_or_none.return_value = None
        return result

    override_db.execute.side_effect = execute_side_effect

    with patch("backend.services.session_service.get_session", return_value={"id": user_id, "session_id": "test"}):
        response = await async_client.delete(
            f"/api/v1/designs/{design_id}/like?session_id=test",
            headers=api_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["success"] is True
