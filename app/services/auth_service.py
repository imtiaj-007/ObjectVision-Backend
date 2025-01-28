from typing import Optional, Dict, Any
from fastapi import Request, Response, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.auth_repository import AuthRepository
from app.repository.session_repository import SessionRepository
from app.db.schemas.user_schema import User

from app.services.user_service import UserService
from app.services.session_service import SessionService
from app.services.password_service import PasswordService
from app.services.token_service import TokenService
from app.models.user_model import (
    UserLogin,
    TokenResponse,
)


class AuthService:    
    @classmethod
    async def get_current_user(
        db: AsyncSession, 
        token: str = Depends(TokenService.oauth2_scheme)
    ) -> Optional[User]:
        """Get current user from token."""
        try:
            # Decode the token to extract user information
            payload = TokenService.verify_token(token)
            username: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            user_role: str = payload.get("role")

            if user_id is None or username is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

            # Use UserRepository to fetch the user details from the database
            user = await AuthRepository.get_user_by_id(db, user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            return user
        except Exception as e:
            print(f"Error in get_current_user: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @classmethod
    async def authenticate_user(
        db: AsyncSession, 
        login_data: UserLogin
    ) -> User:
        """
        Authenticate the user by email and password.
        Includes exception handling and logging.
        """
        try:
            # Attempt to retrieve user by email / username
            user = await AuthRepository.get_user_by_email_or_username(db, login_data.user_key)

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
    async def handle_google_oauth(
        cls, 
        request: Request,
        response: Response,
        db: AsyncSession, 
        token: Dict[str, Any], 
        user_info: Dict[str, Any]
    )-> TokenResponse:
        """Handle Google OAuth tokens and user information to create user_session."""
        
        access_token = token.get("access_token")
        id_token = token.get("id_token")
        email = user_info.get("email")
        name = user_info.get("name")
        
        try:
            user = await AuthRepository.get_user_by_email(db, email)
            if not user:
                user_data: Dict[str, Any] = {
                    "name": name,
                    "email": email,
                    "password": access_token
                }
                user = await UserService.create_user(db, user_data)
            
            oAuth_obj: Dict[str, Any] = {
                "oauth_provider": "Google",
                "access_token": access_token,
                "id_token": id_token,
            }
            return await SessionService.handle_user_session(request, response, db, user, True, True, oAuth_obj)

        except HTTPException as http_error:
            raise http_error

        except Exception as e:
            print(f"Unexpected error during logout: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Logout process failed due to a server error",
            )
        
    @classmethod
    async def logout_user(
        db: AsyncSession,
        user_id: int,
        refresh_token: str,
        all_devices: bool = False
    ) -> None:
        """Logout user by invalidating sessions"""
        try:
            await SessionRepository.invalidate_sessions(db, user_id, refresh_token, all_devices)
        
        except HTTPException as http_error:
            raise http_error

        except Exception as e:
            print(f"Unexpected error during logout: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Logout process failed due to a server error",
            )

