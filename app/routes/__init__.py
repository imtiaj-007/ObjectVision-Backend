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

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, Depends
from app.configuration.ws_manager import WSConnectionManager, get_connection_manager
from app.utils.logger import log


# Create the main router
router = APIRouter()


@router.websocket("/v1/ws/{client_id}")
async def websocket_endpoint( 
    websocket: WebSocket, 
    client_id: str,
    connection_manager: WSConnectionManager = Depends(get_connection_manager)
):
    # Accept the websocket connection first
    await websocket.accept()
    
    # Validate client_id
    if not client_id or len(client_id.strip()) == 0:
        log.warning(f"Rejected WebSocket connection with invalid client_id")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Check if connection already exists
    if await connection_manager.connection_exists(client_id):
        log.warning(f"Duplicate connection attempt for client_id: {client_id}")
        await websocket.send_json({
            "type": "error",
            "message": "Connection with this ID already exists"
        })
        # await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        # return
    
    # Register the connection with Redis
    if not await connection_manager.connect(client_id, websocket):
        log.error(f"Failed to register client {client_id} with connection manager")
        await websocket.send_json({
            "type": "error",
            "message": "Failed to establish connection"
        })
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        return

    # Send confirmation to client
    await websocket.send_json({
        "type": "connection_established",
        "client_id": client_id
    })
    
    try:
        async for message in connection_manager.listen_messages(client_id):
            await connection_manager.refresh_connection(client_id)
            await websocket.send_json(message)
            
    except WebSocketDisconnect:
        log.info(f"Client {client_id} disconnected")
    except Exception as e:
        log.error(f"WebSocket error for client {client_id}: {str(e)}")
    finally:            
        await connection_manager.disconnect(client_id)
        log.info(f"Connection resources cleaned up for client {client_id}")


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
