# auth.py — API Key 认证中间件
# 职责：拦截 /api/v1/ 路径下的请求，验证 X-API-Key 请求头
# 开发模式下（API_KEY 未配置或为空）自动放行

import hmac

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from backend.config import settings
from backend.schemas.common import AUTH_ERROR, api_error
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class APIKeyMiddleware(BaseHTTPMiddleware):
    """API Key 认证中间件 — 仅对 /api/v1/ 路径生效"""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # 非 API 路径直接放行（静态文件、健康检查等）
        if not path.startswith("/api/v1/"):
            return await call_next(request)

        # 开发模式：未配置 API_KEY 时自动放行
        if not settings.API_KEY:
            return await call_next(request)

        api_key = request.headers.get("X-API-Key", "")
        if not api_key or not hmac.compare_digest(api_key, settings.API_KEY):
            logger.warning("认证失败 %s %s", request.method, path)
            from starlette.responses import JSONResponse

            return JSONResponse(status_code=401, content=api_error(AUTH_ERROR, "API Key 缺失或无效"))

        return await call_next(request)
