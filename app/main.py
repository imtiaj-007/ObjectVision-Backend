from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from dotenv import load_dotenv

from app.middleware.request_logger import RequestLoggerMiddleware
from app.db.database import DatabaseConfig, DatabaseManager
from app.scheduler.session_scheduler import lifespan as scheduler_lifespan
from app.handlers.exception import ExceptionHandler
from app.configuration.config import settings
from app.utils.logger import log
from app.docs import app_description
from app.tasks.taskfiles.email_task import send_welcome_email_task

# Load environment variables
load_dotenv()

# Initialize the database configuration & manager
db_config = DatabaseConfig(settings.DATABASE_URL)
db_manager = DatabaseManager(db_config)


@asynccontextmanager
async def combined_lifespan(app: FastAPI):
    """
    Combine lifespan context managers for both the DB and the Scheduler.
    This ensures that both the database connection and the scheduler 
    are properly started and stopped.
    """
    try:
        # Start DB connection
        async with db_manager.lifespan(app):            
            # Start Session Scheduler
            async with scheduler_lifespan(app):
                yield
    finally:
        log.info("✅ Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Object Detection API",
    description=app_description,
    version="1.0.0",
    lifespan=combined_lifespan
)

# Custom exception handler to log Exceptions
exception_handler = ExceptionHandler(app)

# Session middleware for OAuth support
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RequestLogger middleware for logging req-res
app.add_middleware(
    RequestLoggerMiddleware,
    exclude_paths={"/health", "/metrics", "/favicon.ico", "/docs", "/openapi.json"},
    slow_request_threshold=1.0,
    max_body_size=1024 * 100,
    sensitive_headers={"authorization", "cookie", "x-api-key", "session", "csrf"}
)

# Import and include routers
from app.routes import router as api_router
app.include_router(api_router, prefix='/api')


# Health check endpoint
@app.get("/health")
async def health_check(db: AsyncSession = Depends(db_manager.get_db)):
    try:
        # await db.execute(text("SELECT 1"))
        send_welcome_email_task.delay({"email": "imtiaj.dev.kol@gmail.com", "name": "SK Imtiaj Uddin"})
        return {"status": "Database connection healthy"}
    
    except Exception as e:
        print(f"Database health check failed: {e}")
        log.critical(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )