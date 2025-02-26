import requests
from urllib.parse import urlencode
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.handlers.exception import CustomException

from app.configuration.config import settings
from app.db.models.user_model import User
from app.db.models.session_model import UserSession
from app.repository.session_repository import SessionRepository

from app.services.token_service import TokenService
from app.schemas.token_schema import TokenResponse
from app.utils.logger import log


class SessionService:
    @staticmethod
    def detect_device_type(user_agent: str) -> str:
        device_types = {
            "mobile": ["android", "iphone", "ipad", "mobile"],
            "tablet": ["ipad", "tablet"],
            "desktop": ["windows", "macintosh", "linux"],
        }

        user_agent = user_agent.lower()
        for key, patterns in device_types.items():
            if any(pattern in user_agent for pattern in patterns):
                return key
        return "desktop"

    @staticmethod
    async def get_location_by_ip(ip: str) -> Dict:
        try:
            base_url = settings.IP_API_BASE_URL or "https://apiip.net/api/check"
            access_token = settings.IP_API_ACCESS_KEY

            params = {
                "ip": ip,
                "accessKey": access_token,
                "output": "json"
            }
            url = f"{base_url}?{urlencode(params)}"

            # Get location information from ApiIP API
            res = requests.get(url)
            location_response = res.json()

            if location_response and location_response.success == False:
                raise CustomException(f"Error getting location info by IP: {e}")
            
            return location_response
        
        except Exception as e:
            log.error(f"Error getting location info by IP: {e}")
            return {
                "ip": ip,
                "city": "Unknown",
                "country": "Unknown",
                "latitude": None,
                "longitude": None,
            }        
                
    
    @classmethod
    async def get_device_info(cls, ip_address: str, user_agent: str) -> Dict:
        """Get device info form request information"""
        try:
            device_type = cls.detect_device_type(user_agent)
            location = await cls.get_location_by_ip(ip_address)
            return {"device_type": device_type, "location": location}
        
        except Exception as e:
            print(f"Error getting device info: {e}")
            return {
                "device_type": None,
                "location": None
            }
    
    @staticmethod
    async def get_user_session(db: AsyncSession, user_id: int) -> Optional[UserSession]:
        """Get current active user session"""
        try:
            session_details = await SessionRepository.get_session_details(db, user_id)
            return session_details
        
        except HTTPException as http_error:
            raise http_error
        
        except Exception as e:
            print(f"Unexpected error during getting session details for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get session",
            )

    @classmethod
    async def create_user_session(
        cls, 
        request: Request, 
        response: Response, 
        db: AsyncSession, 
        user_data: User, 
        remember_me: bool = False,
        oAuth_obj: Dict[str, Any] = None
    ) -> TokenResponse:
        """Create access, refresh token and store device information"""
        try:
            # Get header information
            ip_address = request.client.host
            user_agent = request.headers.get("User-Agent")            
            device_info = await cls.get_device_info(ip_address, user_agent)

            # Create access and refresh tokens
            user_token = TokenService.create_user_token(user_data)
            refresh_token_expiry = datetime.now(timezone.utc) + timedelta(days=7 if remember_me else 1)
            refresh_token = TokenService.create_refresh_token(user_data, ip_address, user_agent, refresh_token_expiry)           

            # Store new session in DB
            session_data: UserSession = {
                "user_id": user_data.id,
                "access_token": user_token.get('access_token'),
                "refresh_token": refresh_token,
                "user_agent": user_agent,
                "ip_address": ip_address,
                "device_type": device_info.get("device_type"),
                "location": device_info.get("location"),
                "expires_at": refresh_token_expiry
            }
            if oAuth_obj:
                session_data.update(oAuth_obj)
            await SessionRepository.create_new_session(db, session_data)

            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                max_age=(7 if remember_me else 1) * 24 * 60 * 60,
                secure=settings.ENVIORNMENT == 'production',
                samesite="Strict" if settings.ENVIORNMENT == 'production' else "Lax"
            )
            return { **user_token, "refresh_token": refresh_token }
        
        except HTTPException as http_error:
            raise http_error
        
        except Exception as e:
            print(f"Unexpected error during session generation for user {user_data.id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate session",
            )
        
    @staticmethod
    async def update_user_session(
        request: Request, 
        db: AsyncSession, 
        user_data: User, 
        current_session: UserSession
    ) -> TokenResponse:
        """Update access, refresh token and device information"""
        try:                        
            # Check for device conflict
            ip_address = request.client.host
            user_agent = request.headers.get("User-Agent")

            if ip_address == current_session.ip_address and user_agent == current_session.user_agent:
                new_token = TokenService.create_user_token(user_data)
                await SessionRepository.update_access_token(db, current_session, new_token.get('access_token'))
                return { "refresh_token": current_session.refresh_token, **new_token }
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="You are already logged in from another device."                    
                )

        except HTTPException as http_error:
            raise http_error
        
        except Exception as e:
            print(f"Unexpected error during session generation for user {user_data.id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate session",
            )  
        
    @classmethod
    async def handle_user_session(
        cls, 
        request: Request, 
        response: Response, 
        db: AsyncSession, 
        user_data: User, 
        remember_me: bool = False,
        current_session: UserSession = None,
        oAuth_obj: Dict[str, Any] = None
    ) -> TokenResponse:
        """Validate user_session and store device information"""
        try:
            # If user tries to login form old_device
            if current_session:
                return await cls.update_user_session(request, db, user_data, current_session)

            # In case of new_device / fresh_login create a new session for User
            return await cls.create_user_session(request, response, db, user_data, remember_me, oAuth_obj)

        except HTTPException as http_error:
            raise http_error
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to validate session",
            )  

