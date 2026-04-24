# main.py — FastAPI 应用入口
# 职责：创建应用实例、注册中间件、挂载路由、提供前端静态文件服务

import sys
from contextlib import asynccontextmanager
from pathlib import Path

# 确保项目根目录在 sys.path 中，使 `from backend.xxx` 导入正常工作
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.api.router import api_router
from backend.config import settings
from backend.database.connection import close_db, init_db
from backend.middleware.auth import APIKeyMiddleware
from backend.middleware.error_handler import add_error_handlers
from backend.middleware.logging import LoggingMiddleware
from backend.utils.logger import get_logger

logger = get_logger(__name__)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
ENGINE_DIR = Path(__file__).resolve().parent.parent / "engine"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("SIGS 校园共创平台服务启动...")
    try:
        await init_db()
        logger.info("数据库连通性验证通过")
    except Exception as e:
        logger.warning("数据库连通性验证失败: %s（服务仍可启动）", e)
    yield
    await close_db()
    logger.info("服务关闭...")


app = FastAPI(
    title="SIGS Design Agent Game",
    description="AR 校园探索与共创平台",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(APIKeyMiddleware)
app.add_middleware(LoggingMiddleware)
add_error_handlers(app)

app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return RedirectResponse(url="/pages/landing.html")


if ENGINE_DIR.exists():
    app.mount("/engine", StaticFiles(directory=ENGINE_DIR, html=False), name="engine")

if FRONTEND_DIR.exists():
    app.mount("", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
