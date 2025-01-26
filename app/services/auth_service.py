from typing import Optional
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.configuration.config import settings
from app.repository.user_repository import UserRepository
from app.db.schemas.user_schema import User


class AuthService:
    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.TOKEN_EXPIRY or 30
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    @classmethod
    def create_access_token(cls, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""

        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
    
    @classmethod
    def create_refresh_token(cls, user: User, ip_address: str, user_agent: str, expiry: datetime) -> str:
        """Create a refresh token with device-specific info."""
        
        if not user or not user.email or not user.id:
            raise ValueError("Invalid user data")
        
        if not ip_address or not user_agent:
            raise ValueError("IP address and user agent are required")
        
        to_encode = {
            "sub": user.email,
            "user_id": user.id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "exp": expiry
        }

        refresh_token = jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return refresh_token

    @classmethod
    def verify_token(cls, token: str):
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @classmethod
    async def get_current_user(
        cls, db: AsyncSession, token: str = Depends(oauth2_scheme)
    ):
        """Get current user from token."""
        try:
            # Decode the token to extract user information
            payload = cls.verify_token(token)
            username: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            user_role: str = payload.get("role")

            if user_id is None or username is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

            # Use UserRepository to fetch the user details from the database
            user = await UserRepository.get_user_by_id(db, user_id)
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
