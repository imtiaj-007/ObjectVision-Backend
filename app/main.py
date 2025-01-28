from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from dotenv import load_dotenv

from app.configuration.config import settings
from app.db.database import DatabaseConfig, DatabaseManager
from app.scheduler.session_scheduler import lifespan as scheduler_lifespan

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
                print("🔁 Session schedular startup complete - running application")
                yield
    finally:
        print("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Object Detection API",
    description="ML-powered object detection service",
    version="0.1.0",
    lifespan=combined_lifespan
)

# Add session middleware for OAuth support
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.route import router as api_router
app.include_router(api_router, prefix='/api')


# Health check endpoint
@app.get("/health")
async def health_check(db: AsyncSession = Depends(db_manager.get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "Database connection healthy"}
    
    except Exception as e:
        print(f"Database health check failed: {str(e)}")
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