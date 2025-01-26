from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import db_session_manager
from app.services.user_service import UserService
from app.models.user_model import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    TokenResponse,
)


router = APIRouter()

@router.post(
    "/create", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: UserCreate, 
    db: AsyncSession = Depends(db_session_manager.get_db)
):
    """Route to create a user."""
    try:
        return await UserService.create_user(db, user)
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        print(f"Unexpected error in create_user route: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the user",
        )


@router.post(
    "/login", 
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK    
)
async def user_login(
    request: Request,
    response: Response,
    login_data: UserLogin, 
    db: AsyncSession = Depends(db_session_manager.get_db), 
    remember_me: bool = False
) -> TokenResponse:
    """Authenticate user and generate token."""
    try:
        user = await UserService.authenticate_user(db, login_data)
        return UserService.create_user_session(request, response, db, user, remember_me)

    except HTTPException as http_error:
        raise http_error

    except Exception as e:
        print(f"Unexpected error in user_login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while logging in",
        )


@router.put("/update")
async def update_user(
    user_update: UserUpdate, db: AsyncSession = Depends(db_session_manager.get_db)
):
    """Update user profile."""
    # TODO: Implement with proper authentication
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User update not implemented",
    )


@router.delete("/delete")
async def delete_user():
    """Delete user account."""
    # TODO: Implement with proper authentication
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User deletion not implemented",
    )
