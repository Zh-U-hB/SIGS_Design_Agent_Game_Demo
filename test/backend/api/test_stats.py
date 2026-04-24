# test_stats.py — 统计 API 端点测试
# 职责：测试 GET /api/v1/stats 的统计数据返回

from unittest.mock import MagicMock

import pytest


@pytest.mark.asyncio
async def test_get_stats(async_client, override_db, api_headers):
    """GET /api/v1/stats 应返回访客数、设计数、点赞数、覆盖区域数"""
    from database.models import Design, Like, User

    def execute_side_effect(stmt):
        result = MagicMock()
        result.scalar.return_value = 10
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        result.scalars.return_value = scalars_mock
        return result

    override_db.execute.side_effect = execute_side_effect

    response = await async_client.get("/api/v1/stats", headers=api_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "total_visitors" in data["data"]
    assert "total_designs" in data["data"]
    assert "total_likes" in data["data"]
    assert "areas_covered" in data["data"]


@pytest.mark.asyncio
async def test_get_stats_no_auth(async_client):
    """GET /api/v1/stats 无 API Key 应返回 401"""
    response = await async_client.get("/api/v1/stats")
    assert response.status_code == 401
