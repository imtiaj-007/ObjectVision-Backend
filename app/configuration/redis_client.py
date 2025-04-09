import redis
from functools import lru_cache
from app.configuration.config import settings
from app.utils.logger import log


class RedisConnectionError(Exception):
    """Exception raised when Redis connection fails"""
    pass


class RedisClient:
    """Singleton Redis client to provide a global instance."""

    def __init__(self):
        self.client = None

    def connect(self):
        """Establishes a connection to Redis."""
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
            )
            if not self.client.ping():
                raise RedisConnectionError("Failed to ping Redis server")
        except redis.RedisError as e:
            log.critical(f"Failed to connect to Redis: {str(e)}")
            raise RedisConnectionError(f"Redis connection error: {str(e)}")
        except Exception as e:
            log.critical(f"Unexpected error during Redis connection: {str(e)}")
            raise RedisConnectionError(f"Unexpected Redis error: {str(e)}")

    def get_client(self):
        """Returns the Redis client instance."""
        if self.client is None:
            self.connect()
        return self.client


@lru_cache(maxsize=1)
def get_redis_instance():
    """Provides a globally shared Redis instance."""
    redis_client = RedisClient()
    return redis_client.get_client()


# Initialize Redis globally
try:
    redis_instance = get_redis_instance()
    log.info("Redis connection established successfully.")
except RedisConnectionError as e:
    log.critical(f"Global Redis initialization failed: {str(e)}")
    raise
