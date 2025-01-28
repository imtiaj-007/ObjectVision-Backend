from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.db.database import db_session_manager
from app.repository.session_repository import SessionRepository

# Create a global scheduler instance using AsyncIOScheduler instead of BackgroundScheduler
scheduler = AsyncIOScheduler()

async def job_update_expired_sessions():
    """Job to update expired sessions, called periodically."""
    try:
        async with db_session_manager.get_db() as db:
            await SessionRepository.update_expired_sessions(db)
            print("Successfully updated expired sessions")
    except Exception as e:
        print(f"Error updating expired sessions: {str(e)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to start and stop the scheduler.
    
    This manages the scheduler's lifecycle with FastAPI's startup 
    and shutdown events.
    """
    try:
        # Startup logic
        scheduler.add_job(
            job_update_expired_sessions,
            IntervalTrigger(minutes=5),
            id="update_expired_sessions",
            replace_existing=True,
            max_instances=1
        )
        scheduler.start()        
        yield
    
    except Exception as e:
        print(f"Error in scheduler lifecycle: {str(e)}")
        raise
    finally:
        # Shutdown logic
        scheduler.shutdown()
        print("Scheduler shut down")


# Optional: Function to run a one-off job for testing
async def run_job_manually():
    """Helper function to run the job manually for testing."""
    await job_update_expired_sessions()