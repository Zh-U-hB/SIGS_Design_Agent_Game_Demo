# error_handler.py — 全局异常处理中间件
# 职责：统一捕获请求验证错误和未处理异常，返回标准化错误响应

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.schemas.common import BAD_PARAMS, SERVER_ERROR, api_error
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def add_error_handlers(app: FastAPI) -> None:
    """注册全局异常处理器到 FastAPI 应用"""

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """请求参数验证失败 → 返回 40001"""
        logger.warning("参数验证失败 %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(status_code=422, content=api_error(BAD_PARAMS, "请求参数错误"))

    @app.exception_handler(Exception)
    async def global_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """未处理异常 → 返回 50001，记录日志但不泄露内部细节"""
        logger.error("未处理异常 %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(status_code=500, content=api_error(SERVER_ERROR, "服务器内部错误"))
