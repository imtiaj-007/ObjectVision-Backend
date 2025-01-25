from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from dotenv import load_dotenv

from app.middleware.authenticate import AuthenticateUserMiddleware
from app.configuration.config import settings  
from app.db.database import DatabaseConfig, DatabaseManager

# Load environment variables
load_dotenv()

# Initialize the database configuration & manager
db_config = DatabaseConfig(settings.DATABASE_URL)
db_manager = DatabaseManager(db_config)

# Create FastAPI application
app = FastAPI(
    title="Object Detection API",
    description="ML-powered object detection service",
    version="0.1.0",
    lifespan=db_manager.lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    AuthenticateUserMiddleware,
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
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection failed")
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
