from typing import Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.user_repository import UserRepository
from app.repository.auth_repository import AuthRepository

from app.services.password_service import PasswordService
from app.schemas.user_schema import UserRole, UserCreate


class UserService:          
        
    @staticmethod
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
        hashed_password = PasswordService.get_password_hash(user_data.password)

        new_user: Dict[str, Any] = {
            **user_data.model_dump(),
            "password": hashed_password,
            "role": UserRole.USER.value,
            "is_active": True,
            "is_blocked": False
        }
        
        return await UserRepository.create_user(db, new_user)
