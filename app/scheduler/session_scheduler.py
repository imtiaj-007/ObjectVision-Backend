from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.db.database import db_session_manager
from app.services.session_service import SessionService

# Create a global scheduler instance
scheduler = BackgroundScheduler()

async def job_update_expired_sessions():
    """Job to update expired sessions, called periodically."""
    async with db_session_manager.get_db() as db:
        await SessionService.update_expired_sessions(db)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to start and stop the scheduler.
    
    This manages the scheduler's lifecycle with FastAPI's startup 
    and shutdown events.
    """
    # Startup logic
    scheduler.add_job(
        job_update_expired_sessions,
        IntervalTrigger(minutes=5),
        id="update_expired_sessions",
        replace_existing=True,
    )
    scheduler.start()
    
    yield
    
    # Shutdown logic
    scheduler.shutdown()
