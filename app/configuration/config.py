import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # env type
    ENVIORNMENT: str = "development"

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

    # Celery credentials
    CELERY_BROKER_URL: str = "redis://localhost:6379/0" or "pyamqp://guest@localhost//"
    CELERY_BACKEND_URL: str = "redis://localhost:6379/0" or "pyamqp://guest@localhost//"
    MAX_RETRIES: int = 3

    # Queue namings
    LOGGING_QUEUE: str = "logging"
    TOKEN_QUEUE: str = "tokens"
    EMAIL_QUEUE: str = "emails"

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