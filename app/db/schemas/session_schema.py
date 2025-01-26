from pydantic import ConfigDict
from sqlmodel import Field, Relationship, JSON
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import re

from app.db.database import Base
from app.db.schemas.user_schema import User


class UserSession(Base, table=True):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "refresh_token": "token_string",
                "user_agent": "Mozilla/5.0",
                "ip_address": "192.168.1.1",
                "device_type": "mobile",
                "location": "New York, USA",
                "expires_at": "2025-01-01T12:00:00Z"
            }
        }
    )

    __tablename__ = 'user_sessions'

    id: int = Field(default=None, primary_key=True, nullable=False)
    user_id: int = Field(foreign_key="user.id", index=True)  
    refresh_token: str = Field(unique=True, index=True, nullable=True)
    user_agent: str = Field(index=True)
    ip_address: str = Field(max_length=45, index=True)
    is_expired: bool = Field(default=False)
    device_type: Optional[str] = Field(default=None, max_length=50)
    location: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON, description="User location in JSON format")

    created_at: datetime = Field(default_factory= lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None, nullable=True)

    is_active: bool = Field(default=True)
    login_attempts: int = Field(default=0)
    expires_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: User = Relationship(back_populates="sessions")

    
    @classmethod
    def check_expiry(cls):
        """Update `is_expired` if `expires_at` is in the past."""
        if cls.expires_at and datetime.now(timezone.utc) > cls.expires_at:
            cls.is_expired = True

    @classmethod
    def validate_ip_address(cls, ip: str) -> bool:
        """
        Validate both IPv4 and IPv6 address formats.
        
        Supports:
        - Standard IPv4 notation
        - IPv6 full and compressed formats
        """

        # Check for None or empty input
        if not ip or not isinstance(ip, str):
            return False

        # IP validation regex
        ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'        
        ipv6_pattern = r'^(?:(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|::)$|^(?:(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]+)$'
        
        return bool(re.match(ipv4_pattern, ip) or re.match(ipv6_pattern, ip))
    
    @classmethod
    def validate_user_agent(cls, user_agent: str) -> bool:
        """
        Validate user agent string with comprehensive checks.
        
        Validates:
        - Non-empty string
        - Reasonable length (between 10 and 300 characters)
        - Contains valid characters
        - Matches typical user agent pattern
        """

        # Check for None or empty string
        if not user_agent:
            return False
        
        # Check length constraints
        if len(user_agent) < 10 or len(user_agent) > 300:
            return False
        
        # Regex patterns for user agent validation
        patterns = [
            r'^[A-Za-z0-9\.\-_/\(\) ]+$',            
            r'^Mozilla/\d+\.\d+\s*\([^)]+\)\s*(?:AppleWebKit/\d+\.\d+|Gecko/\d+|Trident/\d+)?'
        ]        
        return any(re.match(pattern, user_agent, re.IGNORECASE) for pattern in patterns)
