from typing import Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas.user_schema import User
from app.models.user_model import UserLogin, TokenResponse
from app.repository.user_repository import UserRepository
from app.configuration.security import SecurityConfig


class UserService:
    @staticmethod
    async def authenticate_user(
        db: AsyncSession, 
        login_data: UserLogin
    ) -> User:
        """
        Authenticate the user by email and password.
        Includes exception handling and logging.
        """
        try:
            # Attempt to retrieve user by email
            user = await UserRepository.get_user_by_email(db, login_data.email)
            
            # Verify user existence and password validity
            if not user or not SecurityConfig.verify_password(login_data.password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials. Please check your email and password."
                )
            
            return user

        except HTTPException as http_error:
            raise http_error
        
        except Exception as e:
            print(f"Unexpected error during authentication: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication process failed due to a server error"
            )

    @staticmethod
    def create_user_token(user: User) -> TokenResponse:
        """
        Generate JWT token for authenticated user.
        Includes exception handling.
        """
        try:
            token_data: Dict[str, Any] = {
                "sub": user.username,
                "user_id": user.id,
                "role": user.role
            }
            token = SecurityConfig.create_access_token(token_data)
            return TokenResponse(
                access_token=token,
                token_type="Bearer"
            )
        except Exception as e:
            print(f"Unexpected error during token generation for user {user.id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate access token"
            )
