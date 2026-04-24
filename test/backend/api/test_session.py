# test_session.py — 会话 API 端点测试
# 职责：测试 POST /api/v1/sessions 的创建和响应格式

import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_create_session_returns_session_id(async_client, override_db, api_headers):
    """POST /api/v1/sessions 应返回包含 session_id 的新会话"""
    fake_user_id = uuid.uuid4()
    fake_session_id = str(uuid.uuid4())
    fake_created_at = datetime.now(timezone.utc)

    def refresh_side_effect(obj):
        obj.id = fake_user_id
        obj.session_id = fake_session_id
        obj.created_at = fake_created_at

    override_db.refresh.side_effect = refresh_side_effect

    response = await async_client.post(
        "/api/v1/sessions",
        json={},
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["session_id"] == fake_session_id


@pytest.mark.asyncio
async def test_create_session_response_format(async_client, override_db, api_headers):
    """POST /api/v1/sessions 响应应符合统一格式 {code, message, data}"""
    fake_user_id = uuid.uuid4()
    fake_session_id = str(uuid.uuid4())
    fake_created_at = datetime.now(timezone.utc)

    def refresh_side_effect(obj):
        obj.id = fake_user_id
        obj.session_id = fake_session_id
        obj.created_at = fake_created_at

    override_db.refresh.side_effect = refresh_side_effect

    response = await async_client.post(
        "/api/v1/sessions",
        json={},
        headers=api_headers,
    )

    data = response.json()
    assert "code" in data
    assert "message" in data
    assert "data" in data
    assert data["code"] == 0
    assert data["message"] == "success"


@pytest.mark.asyncio
async def test_create_session_no_auth(async_client):
    """POST /api/v1/sessions 无 API Key 应返回 401"""
    response = await async_client.post("/api/v1/sessions", json={})
    assert response.status_code == 401
