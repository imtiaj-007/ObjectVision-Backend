import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database Configuration with defaults from environment variables
    DB_USER: str = 'postgres'
    DB_PASSWORD: str = ''
    DB_HOST: str = 'localhost'
    DB_NAME: str = 'objectdetection'

    # Machine Learning Configuration
    MODEL_PATH: str = "/path/to/ml/model"
    CONFIDENCE_THRESHOLD: float = 0.5

    # API Settings
    SECRET_KEY: str = 'your_secret_api_key'
    TOKEN_EXPIRY: int = 30

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