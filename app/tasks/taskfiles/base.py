from celery import Task
import asyncio
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.configuration.config import settings
from app.performance.metrics import metrics
from app.utils.logger import log

class BaseTask(Task):
    """Base task with common functionality"""
    abstract = True
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        log.error(f"Task {task_id} failed: {exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        log.info(f"Task {task_id} completed successfully")
        super().on_success(retval, task_id, args, kwargs)


class AsyncDatabaseTask(Task):
    """Base Async task with common functionality"""
    abstract = True
    _engine = None
    _sessionmaker = None
    
    def __init__(self):
        super().__init__()
        if self._engine is None:
            self._engine = create_async_engine(
                settings.DATABASE_URL,
                echo=True,
                future=True,
                pool_pre_ping=True
            )
            self._sessionmaker = async_sessionmaker(
                bind=self._engine,
                expire_on_commit=False,
                class_=AsyncSession
            )

    @asynccontextmanager
    async def get_async_session(self):
        """Provide a transactional scope around a series of operations."""
        if not self._sessionmaker:
            raise RuntimeError("Session maker not initialized")
            
        session = self._sessionmaker()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    def run_async(coro):
        """Safely run an async coroutine in a sync context."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            return loop.run_until_complete(coro)
        finally:
            if loop.is_running():
                loop.close()

    async def cleanup(self):
        """Cleanup database connections"""
        if self._engine:
            await self._engine.dispose()
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        log.error(
            f"Task {task_id} failed",
            extra={
                "task_id": task_id,
                "error": str(exc),
                "args": args,
                "kwargs": kwargs
            },
            exc_info=True
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success"""
        log.info(
            f"Task {task_id} completed successfully",
            extra={
                "task_id": task_id,
                "args": args,
                "kwargs": kwargs,
                "result": retval
            }
        )
        super().on_success(retval, task_id, args, kwargs)