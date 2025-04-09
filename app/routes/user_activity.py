from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from cache.activity_tracker import user_activity_tracker
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
    
    user = auth_obj["user"]
    
    # Check if activities exist in cache
    cached_activities = user_activity_tracker.get_activities(user.username)
    
    if cached_activities:
        activities = [activity for activity in cached_activities.values() if activity is not None]
        if activities:
            return activities
    
    # If not in cache or cache is empty, fetch from database
    activities = await UserActivityService.get_user_activities(db, user.id)
    
    # Store activities in cache
    for activity in activities:
        user_activity_tracker.store_activity(user.username, activity)
    
    return activities