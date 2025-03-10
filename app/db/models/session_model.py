from pydantic import ConfigDict
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, JSON
from datetime import datetime, timezone
from typing import Optional, Dict, Any, TYPE_CHECKING
from app.db.database import Base


if TYPE_CHECKING:
    from app.db.models.user_model import User
    

class UserSession(Base, table=True):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "user_id": 1,
                "access_token": "access_token_string",
                "refresh_token": "token_string",
                "oauth_token": "oauth_token_string",
                "oauth_provider": "google",
                "user_agent": "Mozilla/5.0",
                "ip_address": "192.168.1.1",
                "device_type": "mobile",
                "location": "New York, USA",
                "is_active": True,
                "login_attempts": 0,
                "expires_at": "2025-01-01T12:00:00Z",
            }
        },
    )

    __tablename__ = "user_sessions"
    __table_args__ = {
        'schema': None,
        'keep_existing': True
    }

    id: int = Field(default=None, primary_key=True, nullable=False)
    user_id: int = Field(foreign_key="users.id", index=True)
    access_token: str = Field(unique=True, index=True, nullable=False)
    refresh_token: str = Field(unique=True, index=True, nullable=False)
    oauth_token: Optional[str] = Field(
        default=None, description="Google OAuth ID token"
    )
    oauth_provider: Optional[str] = Field(
        default=None, max_length=50, description="OAuth provider name"
    )
    user_agent: str = Field(min_length=10, max_length=300, default=None, index=False)
    ip_address: str = Field(max_length=45, index=False)
    device_type: Optional[str] = Field(default=None, max_length=50)
    location: Optional[Dict[str, Any]] = Field(
        default=None, sa_type=JSON, description="User location in JSON format"
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=True,
    )

    is_active: bool = Field(default=True)
    login_attempts: int = Field(default=0)
    expires_at: Optional[datetime] = Field(default=None, sa_type=DateTime(timezone=True),)

    # Relationships
    user: "User" = Relationship(back_populates="user_sessions")
    