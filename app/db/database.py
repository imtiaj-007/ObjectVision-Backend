from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator

from fastapi import FastAPI, HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import SQLModel

from app.configuration.config import settings
from app.utils.logger import log


# Base Model for alembic
class Base(SQLModel):
    """Base class for all models"""
    pass


class DatabaseConfig:
    def __init__(self, db_url: str):
        """Initialize database engine and sessionmaker."""
        # Synchronous engine and sessionmaker
        self.sync_engine = create_engine(db_url.replace("+asyncpg", "+psycopg2"), echo=True, future=True)
        self.SyncSessionLocal = sessionmaker(
            bind=self.sync_engine, expire_on_commit=False
        )

        # Asynchronous engine and sessionmaker
        self.async_engine = create_async_engine(db_url, echo=True, future=True)
        self.AsyncSessionLocal = async_sessionmaker(
            bind=self.async_engine, expire_on_commit=False
        )        


class DatabaseManager:
    def __init__(self, db_config: DatabaseConfig):
        self.config = db_config

    @contextmanager
    def get_db_synchronous(self) -> Generator[Session, None, None]:
        """
        Create a synchronous database session context manager.
        
        Returns:
            SQLAlchemy Session object for synchronous database operations
        """
        session = self.config.SyncSessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            log.error(f"❌ Error in DB session: {e}")
            raise
        finally:
            session.close()

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """
        Async lifespan context manager for the database.
        This initializes the database and ensures the connection is closed properly.
        """
        try:
            log.info("✅ Database connection established successfully.")
            yield
        except Exception as e:
            log.error(f"❌ Database startup error: {e}")
            raise
        finally:
            await self.config.async_engine.dispose()
            log.info("✅ Database connection closed.")

    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.config.AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except HTTPException:
                # Re-raise HTTPException without modification
                raise
            except Exception as e:
                await session.rollback()
                log.error(f"❌ Database error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Database error: {e}",
                )
            finally:
                await session.close()


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
    
    @property
    def get_db_synchronous(self):
        """Expose the `get_db_synchronous` method of the DatabaseManager."""
        return self.db_manager.get_db_synchronous


# Global instance for easy access
db_session_manager = DatabaseSessionManager()