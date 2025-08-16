import logging
import os
from functools import lru_cache

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class RedisSettings(BaseSettings):
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_CACHE_TTL: int = int(os.getenv("REDIS_CACHE_TTL", "3600"))  # 1 hour default

    # Cache key prefixes
    CACHE_KEY_PREFIX: str = "intrusion_detector"
    REQUEST_CACHE_PREFIX: str = "request"
    RESPONSE_CACHE_PREFIX: str = "response"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


@lru_cache()
def get_redis_settings() -> RedisSettings:
    try:
        settings = RedisSettings()
        logger.info(f"Redis URL: {settings.REDIS_URL}")
        logger.info("Redis configuration loaded successfully")
        return settings
    except Exception as e:
        logger.error(f"Error loading Redis configuration: {str(e)}")
        raise
