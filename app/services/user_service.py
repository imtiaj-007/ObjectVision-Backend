from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import EmailStr
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.user_repository import UserRepository
from app.repository.auth_repository import AuthRepository

from app.services.password_service import PasswordService
from app.services.otp_service import OTPService
from app.schemas.user_schema import UserCreate, UserData



class UserService:

    @staticmethod
    async def create_user(
        db: AsyncSession, 
        user_data: UserCreate, 
        creator: Optional[UserData] = None
    ) -> Dict[str, Any]:
        """Create a new User"""

        # Check if the user already exists
        existing_user = await AuthRepository.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        # Create the user
        hashed_password = PasswordService.get_password_hash(user_data.password)

        new_user: Dict[str, Any] = {
            **user_data.model_dump(),
            "password": hashed_password,
        }

        user = await UserRepository.create_user(db, new_user)

        if creator:
            #TODO: Send user email and random password, using which he can login first time and reset the password
            pass
        else:
            await OTPService.create_otp(db, user)                                   

        return {
            "status": 1, 
            "message": "User has been created successfully.",
            "user_id": user.id,
            "email": user.email
        }
    