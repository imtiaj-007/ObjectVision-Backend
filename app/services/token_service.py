from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.configuration.config import settings
from app.db.models.user_model import User
from app.schemas.token_schema import AccessToken, RefreshToken, TokenType


class TokenService:
    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.TOKEN_EXPIRY or 30
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


    @classmethod
    def create_access_token(cls, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""

        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode: AccessToken = {
            **data,
            "exp": expire
        }
        return jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
    
    @classmethod
    def create_refresh_token(cls, user: User, ip_address: str, user_agent: str, expiry: datetime) -> str:
        """Create a refresh token with device-specific info."""
        
        if not user or not user.email or not user.id:
            raise ValueError("Invalid user data")
        
        if not ip_address or not user_agent:
            raise ValueError("IP address and user agent are required")
        
        to_encode: RefreshToken = {
            "sub": user.email,
            "user_id": user.id,
            "role": user.role,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "exp": expiry
        }

        refresh_token = jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return refresh_token
    
    @classmethod
    def create_user_token(cls, user: User) -> Dict[str, Any]:
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
            token = cls.create_access_token(token_data)
            return { "access_token": token, "token_type": "Bearer" }

        except HTTPException as http_error:
            raise http_error
        
        except Exception as e:
            print(f"Unexpected error during token generation for user {user.id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate access token",
            )

    def verify_token(cls, token: str, token_type: TokenType = "access"):
        """
        Verify and decode a JWT token with type-specific validation.
        
        Args:
            token: The JWT token string to verify
            token_type: Either "access" or "refresh" to determine validation rules
        """
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            
            if token_type == "refresh":
                required_claims = {"sub", "user_id", "role", "ip_address", "user_agent", "exp"}
                if not all(claim in payload for claim in required_claims):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid refresh token format",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            else:
                required_claims = {"sub", "user_id", "role", "exp"}
                if not all(claim in payload for claim in required_claims):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid access token format",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            
            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"{token_type.title()} token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )    