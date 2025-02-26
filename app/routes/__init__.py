from fastapi import APIRouter
from app.routes.auth import router as auth_router
from app.routes.otp import router as otp_router
from app.routes.user import router as user_router
from app.routes.admin import router as admin_router
from app.routes.detection import router as detection_router
from app.routes.address import router as address_router
from app.routes.phone_number import router as phone_number_router
from app.routes.payment import router as payment_router

# Create the main router
router = APIRouter()

# Include sub-routers
router.include_router(auth_router, prefix="/v1/auth", tags=["Authentication"])
router.include_router(otp_router, prefix="/v1/otp", tags=["OTP"])
router.include_router(user_router, prefix="/v1/user", tags=["User"])
router.include_router(admin_router, prefix="/v1/admin", tags=["Admin"])
router.include_router(detection_router, prefix="/v1/detection", tags=["Detection"])
router.include_router(address_router, prefix="/v1/address", tags=["Address"])
router.include_router(phone_number_router, prefix="/v1/mobile", tags=["Phone Number"])
router.include_router(payment_router, prefix="/v1/payment", tags=["Payment"])
