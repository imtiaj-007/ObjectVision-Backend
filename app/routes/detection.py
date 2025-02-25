from typing import Dict, Any, Optional
from fastapi import APIRouter, UploadFile, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import db_session_manager
from app.services.auth_service import AuthService
from app.services.detection_service import DetectionService


router = APIRouter()


@router.post(
    "/image", 
    response_model=None, 
    status_code=status.HTTP_200_OK,
    summary="Perform detection on images",
)
async def image_detection(
    model_size: str,
    file: UploadFile, 
    # auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user)
):
    # user = auth_obj.get("user")
    return await DetectionService.image_detection(file, model_size)


@router.post(
    "/video", 
    response_model=None, 
    status_code=status.HTTP_200_OK,
    summary="Perform detection on videos",
)
async def video_detection(
    db: AsyncSession = Depends(db_session_manager.get_db),
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user)
):
    pass