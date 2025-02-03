from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.db.database import db_session_manager
from app.repository.session_repository import SessionRepository
from app.utils.logger import log


class SessionScheduler:
    def __init__(self, db_session_manager):
        self.scheduler = AsyncIOScheduler()
        self.db_session_manager = db_session_manager
        self._configure_job()
    
    def _configure_job(self) -> None:
        """Configure the session update job with proper error handling."""
        self.scheduler.add_job(
            self._job_update_expired_sessions,
            IntervalTrigger(minutes=5),
            id="update_expired_sessions",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=300
        )
    
    async def _job_update_expired_sessions(self) -> None:
        """Job to update expired sessions with comprehensive error handling."""
        log.info("♻️  Starting expired sessions update job")
        try:
            async for db in self.db_session_manager.get_db():
                try:
                    updated_count = await SessionRepository.update_expired_sessions(db)
                    
                    msg = ""
                    if(updated_count == 0):
                        msg = "🔰 All sessions are active, no need to update."
                    else:
                        msg = f"✅ Successfully updated {updated_count} expired session{'s' if updated_count > 1 else ''}"
                    
                    log.success(msg)
                
                except Exception as e:
                    log.error(
                        "❌ Error updating expired sessions",
                        exc_info=True,
                        extra={
                            "error_type": type(e).__name__,
                            "error_details": str(e)
                        }
                    )
        except Exception as e:
            log.error(
                "❌ Error in database session",
                exc_info=True,
                extra={"error": str(e)}
            )
    
    async def start(self) -> None:
        """Start the scheduler with error handling."""
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                log.info("✅ Session scheduler started successfully")
        except Exception as e:
            log.error(
                "❌ Failed to start session scheduler",
                exc_info=True,
                extra={"error": str(e)}
            )
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the scheduler gracefully."""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)
                log.info("⏺️ Session scheduler shut down successfully")
        except Exception as e:
            log.error(
                "❌ Error during scheduler shutdown",
                exc_info=True,
                extra={"error": str(e)}
            )
            raise

# Create a global scheduler instance
session_scheduler = SessionScheduler(db_session_manager)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Combined lifespan manager that handles both database and scheduler.
    """
    async with db_session_manager.lifespan(app):
        try:
            await session_scheduler.start()
            yield
        finally:
            await session_scheduler.shutdown()

async def run_job_manually() -> None:
    """Helper function to run the job manually for testing."""
    await session_scheduler._job_update_expired_sessions()
