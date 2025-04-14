from app.configuration.redis_client import get_redis_instance

# Connect to Redis
redis_client = get_redis_instance()

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
