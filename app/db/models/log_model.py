from pydantic import ConfigDict
from sqlmodel import Field, JSON
from sqlalchemy import DateTime
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from app.schemas.log_schema import LogLevel
from app.db.database import Base


class Log(Base, table=True):
    """
    SQLModel schema for storing application logs with comprehensive metadata.
    Includes request details, error information, and performance metrics.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True,
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

    __tablename__ = "logs"
    __table_args__ = {
        'schema': None,
        'keep_existing': True
    }

    # Primary key and basic log information
    id: Optional[int] = Field(default=None, primary_key=True)    
    level: LogLevel = Field(nullable=False, index=True)
    message: str = Field(nullable=False)
    
    # Request context information
    request_id: Optional[str] = Field(default=None, index=True)
    client_host: Optional[str] = Field(default=None, max_length=255)
    client_port: Optional[int] = Field(default=None, nullable=True)
    method: Optional[str] = Field(default=None, max_length=10)
    path: Optional[str] = Field(default=None, max_length=2048)
    
    # List fields for complex data
    query_params: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_type=JSON,
        description="JSON object of query parameters",
    )
    headers: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_type=JSON,
        description="JSON object of request headers",
    )
    
    # Response-related fields
    status_code: Optional[int] = Field(default=None, nullable=True)
    error_details: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_type=JSON,
        description="JSON object of error details",
    )
    stack_trace: Optional[str] = Field(default=None)
    
    # Performance metrics
    duration: Optional[float] = Field(default=None)
    additional_details: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_type=JSON,
        description="JSON object of additional details",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
        index=True
    )