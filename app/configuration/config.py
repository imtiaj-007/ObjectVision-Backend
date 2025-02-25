import os
from pydantic import EmailStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # env type
    ENVIORNMENT: str = "development"
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Frontend URLs
    FRONTEND_BASE_URL: str = "http://localhost:3000"
    FRONTEND_SUCCESS_URL: str = "http://localhost:3000/success"
    FRONTEND_ERROR_URL: str = "http://localhost:3000/error"

    # Database Configuration with defaults from environment variables
    DB_USER: str = 'postgres'
    DB_PASSWORD: str = 'secret_password'
    DB_HOST: str = 'localhost'
    DB_NAME: str = 'objectdetection'

    # Machine Learning Configuration
    MODEL_PATH: str = "/path/to/ml/model"
    CONFIDENCE_THRESHOLD: float = 0.5

    # Google OAuth 2.0 credentials
    GOOGLE_CLIENT_ID: str = 'your_google_oAuth_client_id'
    GOOGLE_CLIENT_SECRET: str = 'your_google_oAuth_client_secret'
    GOOGLE_REDIRECT_URI: str = 'your_google_oAuth_redirect_url'

    # API Settings
    SECRET_KEY: str = 'your_secret_api_key'
    TOKEN_EXPIRY: int = 30

    # Log settings
    LOG_ROTATION: str = "00:00"
    LOG_RETENTION: str = "30 days"

    # Redis Credentials
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}" or "redis://localhost:6379/0"

    # Celery credentials
    CELERY_DB: int = 1
    CELERY_BROKER_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{CELERY_DB}" or "redis://localhost:6379/1"
    CELERY_BACKEND_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{CELERY_DB}" or "redis://localhost:6379/1"
    MAX_RETRIES: int = 3

    # Queue namings
    LOGGING_QUEUE: str = "logging"
    TOKEN_QUEUE: str = "token"
    EMAIL_QUEUE: str = "email"
    DETECTION_QUEUE: str = "detection"

    # IP_API_BASE_URL (If you don't have this Create one for free from here [https://apiip.net/])
    IP_API_BASE_URL: str = "https://apiip.net/api/check"
    IP_API_ACCESS_KEY: str = "your_IP_api_access_key"

    # Brevo Credentials
    BREVO_API_URL: str = "https://api.brevo.com/v3/smtp/email"
    BREVO_API_KEY: str = "your_brevo_api_key"
    EMAIL_SENDER: EmailStr = "imtiaj.dev.kol@gmail.com"
    EMAIL_SENDER_NAME: str ="SK Imtiaj Uddin"
    COMPANY_NAME: str = "ObjectVision"
    SUPPORT_EMAIL: EmailStr = "imtiaj.dev.kol@gmail.com"

    # Async SQLAlchemy Database URL
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.DB_NAME}"

    # Additional settings
    SQL_ECHO: bool = False
    DEBUG: bool = False

    # Configure the location of the .env file (based on environment)
    class Config:
        env_file = ".env"  

def load_settings(environment: str = "development") -> Settings:
    env_file = f".env.{environment}"
    settings = Settings(_env_file=env_file)
    return settings

# Example usage:
environment = os.getenv('ENVIRONMENT', 'development')
settings = load_settings(environment)