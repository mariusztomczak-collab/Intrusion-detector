import redis
import json
import hashlib
import logging
import pandas as pd
from typing import Optional, Dict, Any
from src.core.config.redisconfig import get_redis_settings

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        settings = get_redis_settings()
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True
        )
        self.cache_ttl = settings.REDIS_CACHE_TTL
        self.cache_prefix = settings.CACHE_KEY_PREFIX
        
    def _generate_cache_key(self, features: Dict[str, Any], user_id: str) -> str:
        """Generate a unique cache key based on features and user_id."""
        # Create a hash of the features to ensure consistent key generation
        features_str = json.dumps(features, sort_keys=True)
        hash_input = f"{user_id}:{features_str}"
        hash_value = hashlib.md5(hash_input.encode()).hexdigest()
        return f"{self.cache_prefix}:{hash_value}"
    
    def get_cached_response(self, features: Dict[str, Any], user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached response for given features and user."""
        try:
            cache_key = self._generate_cache_key(features, user_id)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                logger.info(f"Cache hit for key: {cache_key}")
                return json.loads(cached_data)
            else:
                logger.info(f"Cache miss for key: {cache_key}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting cached response: {str(e)}")
            return None
    
    def cache_response(self, features: Dict[str, Any], user_id: str, response: Dict[str, Any]) -> bool:
        """Cache response for given features and user."""
        try:
            cache_key = self._generate_cache_key(features, user_id)
            cache_data = {
                "features": features,
                "user_id": user_id,
                "response": response,
                "cached_at": str(pd.Timestamp.now())
            }
            
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(cache_data)
            )
            
            logger.info(f"Cached response for key: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching response: {str(e)}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            keys = self.redis_client.keys(f"{self.cache_prefix}:*")
            return {
                "total_cached_items": len(keys),
                "cache_prefix": self.cache_prefix,
                "cache_ttl": self.cache_ttl
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {"error": str(e)}
    
    def clear_cache(self) -> bool:
        """Clear all cached items."""
        try:
            keys = self.redis_client.keys(f"{self.cache_prefix}:*")
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} cached items")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False
    
    def ping(self) -> bool:
        """Test Redis connection."""
        try:
            return self.redis_client.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {str(e)}")
            return False

# Create a singleton instance
redis_client = RedisClient()

def get_redis_client() -> RedisClient:
    """Get the singleton Redis client instance."""
    return redis_client 