from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel

from app.configuration.config import settings


# Base Model for alembic
Base = SQLModel

class DatabaseConfig:
    def __init__(self, db_url: str):
        """Initialize database engine and sessionmaker."""
        self.engine = create_async_engine(db_url, echo=True, future=True)
        self.SessionLocal = async_sessionmaker(
            bind=self.engine, expire_on_commit=False
        )


class DatabaseManager:
    def __init__(self, db_config: DatabaseConfig):
        self.config = db_config

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """
        Async lifespan context manager for the database.
        This initializes the database and ensures the connection is closed properly.
        """
        try:
            print("✅ Database connection established successfully.")
            yield
        except Exception as e:
            print(f"❌ Database startup error: {e}")
            raise
        finally:
            await self.config.engine.dispose()
            print("✅ Database connection closed.")

    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.config.SessionLocal() as session:
            try:
                await session.commit() 
                yield session 
            except HTTPException:
                # Re-raise HTTPException without modification
                raise
            except Exception as e:
                await session.rollback() 
                print(f"❌ Database error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Database error: {e}",
                )
            finally:
                pass


class DatabaseSessionManager:
    """
    Singleton pattern for database session manager.
    This ensures a single instance of `DatabaseConfig` and `DatabaseManager` is used.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            db_config = DatabaseConfig(settings.DATABASE_URL)
            cls._instance.db_manager = DatabaseManager(db_config)
        return cls._instance

    @property
    def get_db(self):
        """Expose the `get_db` method of the DatabaseManager."""
        return self.db_manager.get_db

    @property
    def lifespan(self):
        """Expose the `lifespan` method of the DatabaseManager."""
        return self.db_manager.lifespan


# Global instance for easy access
db_session_manager = DatabaseSessionManager()
