from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status

from app.routes.auth import router as auth_router
from app.routes.otp import router as otp_router
from app.routes.user import router as user_router
from app.routes.admin import router as admin_router
from app.routes.detection import router as detection_router
from app.routes.address import router as address_router
from app.routes.phone_number import router as phone_number_router
from app.routes.payment import router as payment_router
from app.routes.subscription import router as subscription_router
from app.routes.user_activity import router as user_activity_router
from app.routes.file_url import router as file_router

from cache import local_storage
from app.utils.logger import log


# Create the main router
router = APIRouter()


@router.websocket("/v1/ws/{client_id}")
async def websocket_detection(
    websocket: WebSocket, 
    client_id: str
):
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="client_id is required to establist socket-connection."
        )
    await websocket.accept()
    local_storage.active_connections[client_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()            
            await websocket.send_json({
                "status": "received", 
                "message": "Keeping connection alive"
            })
    
    except WebSocketDisconnect:
        log.info(f"Client {client_id} disconnected")
    
    except Exception as e:
        log.error(f"WebSocket error: {str(e)}")
    
    finally:
        if client_id in local_storage.active_connections:
            del local_storage.active_connections[client_id]


# Include sub-routers
router.include_router(auth_router, prefix="/v1/auth", tags=["Authentication"])
router.include_router(otp_router, prefix="/v1/otp", tags=["OTP"])
router.include_router(user_router, prefix="/v1/user", tags=["User"])
router.include_router(admin_router, prefix="/v1/admin", tags=["Admin"])
router.include_router(detection_router, prefix="/v1/detection", tags=["Detection"])
router.include_router(address_router, prefix="/v1/address", tags=["Address"])
router.include_router(phone_number_router, prefix="/v1/mobile", tags=["Phone Number"])
router.include_router(payment_router, prefix="/v1/payment", tags=["Payment"])
router.include_router(subscription_router, prefix="/v1/subscription", tags=["Subscription Management"])
router.include_router(user_activity_router, prefix="/v1/user-activity", tags=["User Plan and Activities"])
router.include_router(file_router, prefix="/v1/files", tags=["Local & Cloud Files"])
