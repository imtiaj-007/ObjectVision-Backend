from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import db_session_manager
from app.repository.user_repository import UserRepository
from app.services.user_service import UserService
from app.models.user_model import UserCreate, UserLogin, UserUpdate, UserResponse, TokenResponse


router = APIRouter()

@router.post("/create", response_model=UserResponse)
async def create_user(
    user: UserCreate, 
    db: AsyncSession = Depends(db_session_manager.get_db),
    status_code=status.HTTP_201_CREATED   
):
    # Check if user exists
    existing_user = await UserRepository.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User with this email already exists"
        )
    
    # Create user
    created_user = await UserRepository.create_user(db, user)
    return created_user

@router.post("/login", response_model=TokenResponse)
async def user_login(
    login_data: UserLogin, 
    db: AsyncSession = Depends(db_session_manager.get_db),
    status_code=status.HTTP_200_OK 
):
    """Authenticate user and generate token."""
    try:
        user = await UserService.authenticate_user(db, login_data)
        return UserService.create_user_token(user)
    
    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        print(f"Unexpected error in user_login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while logging in"
        )

@router.put("/update")
async def update_user(
    user_update: UserUpdate, 
    db: AsyncSession = Depends(db_session_manager.get_db)
):
    """Update user profile."""
    # TODO: Implement with proper authentication
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, 
        detail="User update not implemented"
    )

@router.delete("/delete")
async def delete_user():
    """Delete user account."""
    # TODO: Implement with proper authentication
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, 
        detail="User deletion not implemented"
    )