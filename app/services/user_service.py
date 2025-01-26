from typing import Dict, Any
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas.user_schema import User
from app.db.schemas.session_schema import UserSession

from app.repository.user_repository import UserRepository
from app.repository.session_repository import SessionRepository

from app.services.auth_service import AuthService
from app.services.password_service import PasswordService
from app.services.session_service import SessionService

from app.models.user_model import UserLogin, TokenResponse
from app.models.user_model import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    TokenResponse,
)


class UserService:
    @classmethod
    async def authenticate_user(db: AsyncSession, login_data: UserLogin) -> User:
        """
        Authenticate the user by email and password.
        Includes exception handling and logging.
        """
        try:
            # Attempt to retrieve user by email
            user = await UserRepository.get_user_by_email(db, login_data.email)

            # Verify user existence and password validity
            if not user or not PasswordService.verify_password(
                login_data.password, user.password
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials. Please check your email and password.",
                )

            return user

        except HTTPException as http_error:
            raise http_error

        except Exception as e:
            print(f"Unexpected error during authentication: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication process failed due to a server error",
            )

    @classmethod
    def create_user_token(user: User) -> TokenResponse:
        """
        Generate JWT token for authenticated user.
        Includes exception handling.
        """
        try:
            token_data: Dict[str, Any] = {
                "sub": user.username,
                "user_id": user.id,
                "role": user.role,
            }
            token = AuthService.create_access_token(token_data)
            return TokenResponse(access_token=token, token_type="Bearer")
        except Exception as e:
            print(f"Unexpected error during token generation for user {user.id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate access token",
            )
    
    @classmethod
    async def create_user_session(
        cls, 
        request: Request, 
        response: Response, 
        db: AsyncSession, 
        user_data: User, 
        remember_me: bool = False
    ) -> TokenResponse:
        """Create access, refresh token and store device information"""
        try:
            ip_address = request.client.host
            user_agent = request.headers.get("User-Agent")

            # Check last user session
            session_details = await SessionRepository.get_session_details(db, user_data.id)
            if session_details:
                # TODO: need to implement logic and edge cases                
                pass

            # Create access token
            access_token = cls.create_user_token(user_data)

            # Create refresh token with custom expiration based on remember me
            refresh_token_days = 7 if remember_me else 1
            expiry = datetime.now(timezone.utc) + timedelta(days=refresh_token_days) 
            refresh_token = AuthService.create_refresh_token(user_data, ip_address, user_agent, expiry)

            # Get Device information
            device_type = SessionService.detect_device_type(user_agent)
            location = await SessionService.get_location_by_ip(ip_address)

            # Store new session in DB
            session_data: UserSession = {
                "user_id": user_data.id,
                "refresh_token": refresh_token,
                "user_agent": user_agent,
                "ip_address": ip_address,
                "device_type": device_type | None,
                "location": location | None,
                "expires_at": expiry
            }
            await SessionRepository.create_new_session(db, session_data)

            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                max_age=refresh_token_days * 24 * 60 * 60,
                secure=True,
                samesite="Strict"
            )
            return { "access_token": access_token, "token_type": "Bearer" }
        
        except Exception as e:
            print(f"Unexpected error during session generation for user {user_data.id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate session",
            )


    @classmethod
    async def create_user(db: AsyncSession, user_data: UserCreate):
        """Create a new User"""
        # Check if the user already exists
        existing_user = await UserRepository.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        # Create the user
        return await UserRepository.create_user(db, user_data)
