"""
Configuration Management

role: 应用配置管理，从环境变量加载配置
depends: []
exports: [Settings, get_settings]
status: PENDING

functions:
- get_settings() -> Settings: 获取配置单例
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 数据库配置
    database_url: str = "postgresql://user:password@localhost:5432/paper_detection"

    # Redis配置
    redis_url: str = "redis://localhost:6379/0"

    # Deepseek API配置
    deepseek_api_key: str = ""
    deepseek_api_base: str = "https://api.deepseek.com"

    # 文件存储配置
    upload_dir: str = "/data/uploads"
    result_dir: str = "/data/results"
    max_upload_size: int = 100 * 1024 * 1024  # 100MB

    # Celery配置
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
