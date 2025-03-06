from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import db_session_manager
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.schemas.user_schema import (
    UserCreate,
    UserUpdate,
    UserRole,
    UserCreateResponse,
    UserProfile,
    UserInfo,
)
from app.schemas.general_schema import SuccessResponse
from app.docs.descriptions import user_desc
from app.docs.responses import user_res


router = APIRouter()


def optional_auth(auth_service=Depends(AuthService.authenticate_user)):
    """
    Dependency that makes authentication optional.
    Returns None if no valid auth token is present.
    """
    try:
        return auth_service
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return None


@router.post(
    "/create",
    response_model=UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses=user_res.CREATE_USER_RESPONSES,
    summary="Create New User",
    description=user_desc.CREATE_USER_DESCRIPTION,
)
async def create_user(
    user: UserCreate,
    response: Response,
    db: AsyncSession = Depends(db_session_manager.get_db),
    auth_obj: Optional[Dict[str, Any]] = Depends(optional_auth),
):
    """
    Route to create a user. Handles both authenticated and unauthenticated requests.
    For unauthenticated requests (sign-ups), additional validation is performed.
    For authenticated requests (admin creating users), admin privileges are checked.
    """
    if auth_obj is None:
        # Handle unauthenticated user [sign-up scenario]
        if not user.email or not user.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and Password is required for sign-up",
            )
        return await UserService.create_user(db, user)

    else:
        # Handle authenticated user creation [admin/sub-admin]
        auth_user = auth_obj["user"]
        if auth_user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can create users",
            )
        new_access_token = auth_obj["new_access_token"]
        response.headers["Authorization"] = f"Bearer {new_access_token}"
        return await UserService.create_user(db, user, creator=auth_user)


@router.put("/update/{user_id}")
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(db_session_manager.get_db),
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
):
    """Update user profile."""
    # TODO: Implement with proper authentication
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User update not implemented",
    )


@router.delete("/delete/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(db_session_manager.get_db),
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
):
    """Delete user account."""
    # TODO: Implement with proper authentication
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User deletion not implemented",
    )


@router.get("/get-profile")
async def get_user(
    db: AsyncSession = Depends(db_session_manager.get_db),
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
) -> Optional[UserProfile]:
    """Retrieves the authenticated user's information."""
    if not auth_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    return await UserService.get_user_profile(db, auth_obj["user"])


@router.get("/get-usernames")
async def get_all_usernames(
    db: AsyncSession = Depends(db_session_manager.get_db),
) -> List[str]:
    """Retrieves list of all usernames."""

    return await UserService.fetch_usernames(db)


@router.post("/newUser-info")
async def store_new_user_info(
    user_info: UserInfo,
    db: AsyncSession = Depends(db_session_manager.get_db),
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
) -> SuccessResponse:
    """Retrieves the authenticated user's information."""

    if not auth_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    await UserService.store_user_info(db, user_info, auth_obj["user"])
    return {"message": "User Info sored successfully."}
