from typing import Dict, Any, Annotated
from fastapi import Request, Response, HTTPException, Depends, status, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.auth_repository import AuthRepository
from app.repository.session_repository import SessionRepository
from app.db.database import db_session_manager

from app.services.user_service import UserService
from app.services.session_service import SessionService
from app.services.password_service import PasswordService
from app.services.token_service import TokenService

from app.schemas.user_schema import UserLogin, UserCreate, UserData
from app.schemas.token_schema import TokenResponse


security = HTTPBearer() # FastAPI provides built-in Bearer token extraction

class AuthService:    
    @staticmethod
    async def get_user(
        db: AsyncSession = Depends(db_session_manager.get_db), 
        payload: Dict[str, Any] = None
    ) -> UserData:
        """Extract token and send User details"""
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token is required"
            )
        
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        user_role: str = payload.get("role")

        if user_id is None or username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid access_token."
            )
        
        user = await AuthRepository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    @classmethod
    async def authenticate_user(
        cls, 
        auth: HTTPAuthorizationCredentials = Depends(security),
        refresh_token: Annotated[str | None, Cookie()] = None
    ) -> Dict[str, Any]:
        """Get current user from token."""
        try:
            token = auth.credentials
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Access token missing."
                )
            
            payload = TokenService.verify_token(token, "access_token")
            user = await cls.get_user(payload=payload)                       

            return { "user": user }
        
        except HTTPException as http_error:
            if http_error.status_code == 401 and refresh_token:
                # Access token expired, check refresh token
                try:
                    payload = TokenService.verify_token(refresh_token, "refresh_token")
                    user = await cls.get_user(payload=payload)
                    new_access_token = TokenService.create_access_token({
                        "sub": user.username,
                        "user_id": user.id,
                        "role": user.role,
                    })

                    return {
                        "user": user,
                        "new_access_token": {
                            "access_token": new_access_token,
                            "token_type": "Bearer",
                        }
                    }
                
                except HTTPException:
                    raise HTTPException(status_code=401, detail="Refresh token expired")
            else:
                raise

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    async def verify_user_credentials(
        db: AsyncSession, 
        login_data: UserLogin
    ) -> UserData:
        """
        Authenticate the user by email and password.
        Includes exception handling and logging.
        """

        # Attempt to retrieve user by email / username
        user = await AuthRepository.get_user_by_email_or_username(db, login_data.user_key)

        # Verify user existence and password validity
        if not user or not PasswordService.verify_password(login_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials. Please check your email and password.",
            )
        return user

    
    @staticmethod
    async def handle_google_oauth(
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

        if not email or not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email / password is missing",
            )
        
        try:
            user = await AuthRepository.get_user_by_email(db, email)
            if not user:
                data: Dict[str, Any] = {
                    "name": name,
                    "email": email,
                    "password": email
                }
                user_data = UserCreate(**data)
                user = await UserService.create_user(db, user_data)
            
            oAuth_obj: Dict[str, Any] = {
                "oauth_provider": "Google",
                "access_token": access_token,
                "id_token": id_token,
            }
            current_session = await SessionService.get_user_session(db, user.id)
            return await SessionService.handle_user_session(request, response, db, user, True, current_session, oAuth_obj)

        except HTTPException as http_error:
            raise http_error

        except Exception as e:
            print(f"Unexpected error during OAuth callback: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth failed due to a server error",
            )
        
    @staticmethod
    async def logout_user(
        db: AsyncSession,
        user_id: int,
        refresh_token: str = None,
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

