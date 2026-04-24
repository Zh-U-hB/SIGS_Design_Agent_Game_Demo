# config.py — 应用配置管理
# 职责：通过 pydantic-settings 读取 .env 环境变量，提供全局配置单例

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    DATABASE_NAME: str = ""
    API_KEY: str = ""
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    LLM_API_KEY: str = ""
    LLM_API_URL: str = ""
    LLM_MODEL: str = ""
    IMAGE_API_KEY: str = ""
    IMAGE_API_URL: str = ""
    IMAGE_MODEL: str = ""
    MODEL3D_API_KEY: str = ""
    MODEL3D_API_URL: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
