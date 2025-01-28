from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.user_repository import UserRepository
from app.repository.auth_repository import AuthRepository
from app.models.user_model import (
    UserCreate,
)


class UserService:          
        
    @classmethod
    async def create_user(db: AsyncSession, user_data: UserCreate):
        """Create a new User"""
        # Check if the user already exists
        existing_user = await AuthRepository.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        # Create the user
        return await UserRepository.create_user(db, user_data)
