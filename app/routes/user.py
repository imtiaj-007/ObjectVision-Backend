from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import db_session_manager
from app.services.user_service import UserService
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse


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
