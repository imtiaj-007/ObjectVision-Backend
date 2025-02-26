from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.user_repository import UserRepository
from app.repository.auth_repository import AuthRepository
from app.repository.phone_number_repository import PhoneRepository
from app.repository.address_repository import AddressRepository

from app.services.password_service import PasswordService
from app.services.otp_service import OTPService
from app.schemas.user_schema import UserCreate, UserData, UserProfile, UserInfo
from app.schemas.phone_schema import PhoneNumberCreate
from app.schemas.address_schema import AddressCreate


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

    @staticmethod
    async def get_user_profile(
        db: AsyncSession,
        user_data: UserData
    ) -> Optional[UserProfile]:
        """ Returns User Profile details like, user details, Addresses and Phone Numbers etc. """
        
        return await UserRepository.get_profile(db, user_data.id)
    
    @staticmethod
    async def fetch_usernames(
        db: AsyncSession,
    ) -> List[str]:
        """ Returns list of all available usernames. """
        
        return await UserRepository.get_usernames(db)
    
    @staticmethod
    async def store_user_info(
        db: AsyncSession,
        user_info: UserInfo,
        user_data: UserData
    ) -> None:
        """ Returns list of all available usernames. """
        
        # Add username in user_details table
        u_data = { "username": user_info.username }
        await UserRepository.update_user(db, user_data.id, u_data)

        # Store Phone Number
        phone = user_info.phone_number.model_dump()
        p_data = PhoneNumberCreate(
            **phone, 
            user_id=user_data.id
        )
        await PhoneRepository.create_phone(db, phone_data=p_data)

        # Store Address Information
        address = user_info.address.model_dump()
        a_data = AddressCreate(
            **address, 
            user_id=user_data.id
        )
        await AddressRepository.create_address(db, address_data=a_data)
