import redis as SyncRedis
import redis.asyncio as AsyncRedis
from functools import lru_cache
from app.configuration.config import settings
from app.utils.logger import log


class RedisConnectionError(Exception):
    """Exception raised when Redis connection fails"""
    pass


class AsyncRedisClient:
    """Singleton async Redis client to provide a global instance."""

    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Redis client (non-async)"""
        try:
            self.client = AsyncRedis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
            )
            log.info("Async Redis client initialized")
        except Exception as e:
            log.critical(f"Failed to initialize Redis client: {str(e)}")
            raise RedisConnectionError(f"Redis initialization error: {str(e)}")
    
    def get_client(self) -> AsyncRedis:
        """Returns the Redis client instance."""
        if self.client is None:
            self._initialize_client()
        return self.client


class RedisClient:
    """Singleton Redis client to provide a global instance."""

    def __init__(self):
        self.client = None

    def connect(self):
        """Establishes a connection to Redis."""
        try:
            self.client = SyncRedis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
            )
            if not self.client.ping():
                raise RedisConnectionError("Failed to ping Redis server")
            
        except SyncRedis.RedisError as e:
            log.critical(f"Failed to connect to Redis: {str(e)}")
            raise RedisConnectionError(f"Redis connection error: {str(e)}")
        
        except Exception as e:
            log.critical(f"Unexpected error during Redis connection: {str(e)}")
            raise RedisConnectionError(f"Unexpected Redis error: {str(e)}")

    def get_client(self) -> SyncRedis:
        """Returns the Redis client instance."""
        if self.client is None:
            self.connect()
        return self.client


# Single sync global instance
_redis_client = RedisClient()

@lru_cache(maxsize=1)
def get_redis_instance():
    """Provides a globally shared Redis instance."""
    return _redis_client.get_client()


# Single async global instance
_async_redis_client = AsyncRedisClient()

@lru_cache(maxsize=1)
def get_async_redis_instance():
    """Provides a globally shared Redis instance."""
    return _async_redis_client.get_client()