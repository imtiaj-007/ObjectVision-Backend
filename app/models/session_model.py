from pydantic import BaseModel, Field, IPvAnyAddress
from typing import Optional, Annotated
from datetime import datetime


# Base Session Model (Shared Fields)
class SessionBase(BaseModel):
    user_id: int = Field(..., example=1, description="The ID of the associated user")    
    user_agent: Annotated[
        str,
        Field(
            min_length=10, max_length=300, 
            example="Mozilla/5.0 (Windows NT 10.0; Win64; x64)", 
            description="User agent string from the client"
        ),
    ]
    ip_address: IPvAnyAddress = Field(
        ..., example="192.168.1.1", description="IP address of the client initiating the session"
    )
    device_type: Optional[str] = Field(
        None, max_length=50, example="mobile", description="Type of device used for the session"
    )
    location: Optional[str] = Field(
        None, max_length=100, example="New York, USA", description="Geographical location of the client"
    )

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "user_id": 1,
                "refresh_token": "sample_refresh_token_12345",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "ip_address": "192.168.1.1",
                "device_type": "desktop",
                "location": "San Francisco, USA",
            }
        }


# Create Session (Input for Creating a New Session)
class SessionCreate(SessionBase):
    refresh_token: Annotated[
        str,
        Field(
            min_length=20, max_length=255, 
            example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", 
            description="Refresh token for the session"
        ),
    ]
    expires_at: Optional[datetime] = Field(
        None, example="2025-01-01T12:00:00Z", description="Timestamp when the session will expire"
    )


# Update Session (Input for Updating an Existing Session)
class SessionUpdate(BaseModel):
    refresh_token: Optional[
        Annotated[
            str,
            Field(
                min_length=20, max_length=255, 
                example="new_refresh_token_12345", 
                description="Updated refresh token for the session"
            ),
        ]
    ]
    is_expired: Optional[bool] = Field(None, example=True, description="Mark session as expired or not")
    location: Optional[str] = Field(
        None, max_length=100, example="Los Angeles, USA", description="Updated location of the session"
    )
    device_type: Optional[str] = Field(
        None, max_length=50, example="tablet", description="Updated device type of the session"
    )


# Session Response (Output for API Responses)
class SessionResponse(SessionBase):
    id: int = Field(..., example=123, description="Unique identifier of the session")
    is_expired: bool = Field(default=False, example=False, description="Indicates if the session is expired")
    created_at: datetime = Field(
        ..., example="2025-01-22T10:00:00Z", description="Timestamp when the session was created"
    )
    updated_at: Optional[datetime] = Field(
        None, example="2025-01-23T10:00:00Z", description="Timestamp when the session was last updated"
    )

    class Config:
        from_attributes = True
