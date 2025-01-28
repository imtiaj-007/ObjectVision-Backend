from app.configuration.config import settings


class SecurityConfig:
    # Security configurations
    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.TOKEN_EXPIRY or 30