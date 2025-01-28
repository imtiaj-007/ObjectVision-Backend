from fastapi import APIRouter
from app.route.auth import router as auth_router
from app.route.user import router as user_router
from app.route.admin import router as admin_router

# Create the main router
router = APIRouter()

# Include sub-routers
router.include_router(auth_router, prefix="/v1/auth", tags=["Authentication"])
router.include_router(user_router, prefix="/v1/user", tags=["User"])
router.include_router(admin_router, prefix="/v1/admin", tags=["Admin"])
