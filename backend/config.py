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
    LLM_API_KEY: str = ""
    LLM_API_URL: str = ""
    LLM_MODEL: str = "gpt-4"
    IMAGE_API_KEY: str = ""
    IMAGE_API_URL: str = ""
    IMAGE_MODEL: str = "stable-diffusion-xl"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
