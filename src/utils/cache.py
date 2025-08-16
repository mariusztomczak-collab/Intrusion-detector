import structlog
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

logger = structlog.get_logger()


async def init_cache():
    """Initialize Redis cache."""
    try:
        redis = aioredis.from_url(
            "redis://localhost:6379/0", encoding="utf8", decode_responses=True
        )
        FastAPICache.init(RedisBackend(redis), prefix="intrusion-detector-cache")
        logger.info("Successfully initialized Redis cache")
    except Exception as e:
        logger.error("Failed to initialize Redis cache", error=str(e))
        raise


def get_cache_key(traffic_data: dict) -> str:
    """Generate a cache key from traffic data."""
    # Sort the dictionary to ensure consistent key generation
    sorted_data = dict(sorted(traffic_data.items()))
    return f"traffic_analysis:{hash(str(sorted_data))}"


# Cache decorator with 1 hour expiration
cache_decorator = cache(expire=3600)
