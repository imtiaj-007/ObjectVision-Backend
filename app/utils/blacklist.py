import redis
from app.configuration.config import settings

# Connect to Redis
redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST, 
    port=settings.REDIS_PORT, 
    db=settings.REDIS_DB, 
    decode_responses=True
)


def add_token_to_blacklist(token: str, expiry: int):
    """
    Add token to blacklist with expiration.
    """
    redis_client.setex(token, expiry, "blacklisted")


def is_token_blacklisted(token: str) -> bool:
    """
    Check if the token is blacklisted.
    """
    return redis_client.exists(token) == 1
