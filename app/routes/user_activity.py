from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import db_session_manager
from app.services.auth_service import AuthService
from app.services.user_activity_service import UserActivityService

from app.schemas.user_activity_schemas import ActiveUserPlanResponse, UserActivityResponse


router = APIRouter()


# User Subscription Plan routes
@router.get(
    "/plans",
    response_model=List[ActiveUserPlanResponse],
    status_code=status.HTTP_200_OK,
)
async def get_user_plans(
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
    db: AsyncSession = Depends(db_session_manager.get_db),
):
    """Get list of User plans purchased by the user"""
    if not auth_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user."
        )
    return await UserActivityService.get_user_subscription_plans(
        db, auth_obj["user"].id
    )


@router.get(
    "/active-plans",
    response_model=List[ActiveUserPlanResponse],
    status_code=status.HTTP_200_OK,
)
async def get_user_plans(
    is_active: bool = Query(True),
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
    db: AsyncSession = Depends(db_session_manager.get_db),
):
    """Get list of User plans purchased by the user"""
    if not auth_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user."
        )
    return await UserActivityService.get_active_user_subscription_plans(
        db, auth_obj["user"].id, is_active
    )


# User Activity routes
@router.get(
    "/activities",
    response_model=List[UserActivityResponse],
    status_code=status.HTTP_200_OK,
)
async def get_user_plans(
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
    db: AsyncSession = Depends(db_session_manager.get_db),
):
    """Get list of User plans purchased by the user"""
    if not auth_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user."
        )
    return await UserActivityService.get_user_activities(
        db, auth_obj["user"].id
    )