from typing import Optional
from pydantic import BaseModel, EmailStr, Field, StringConstraints
from typing_extensions import Annotated
from datetime import datetime
from app.db.schemas.user_schema import UserRole


# Base User Model (Shared Fields)
class UserBase(BaseModel):
    username: Annotated[
        str, 
        StringConstraints(min_length=3, max_length=50)
    ] = Field(
        ...,
        example="john_doe",
        description="Unique username for the user (3-50 characters)."
    )
    email: EmailStr = Field(
        ...,
        example="user@example.com",
        description="Valid email address of the user."
    )
    mobile: Optional[Annotated[
        str,
        StringConstraints(min_length=10, max_length=15)
    ]] = Field(
        None,
        example="1234567890",
        description="Mobile number of the user (optional, 10-15 digits)."
    )

    class Config:
        from_attributes = True


# Create User (Input for Creating Users)
class UserCreate(UserBase):
    password: Annotated[
        str,
        StringConstraints(min_length=8, max_length=64)
    ] = Field(
        ...,
        example="securepassword",
        description="Password for the user (8-64 characters)."
    )


# Update User (Input for Updating Users)
class UserUpdate(BaseModel):
    username: Optional[Annotated[
        str, 
        StringConstraints(min_length=3, max_length=50)
    ]] = Field(
        None,
        example="new_username",
        description="Updated username for the user (optional, 3-50 characters)."
    )
    email: Optional[EmailStr] = Field(
        None,
        example="new_email@example.com",
        description="Updated email address of the user (optional)."
    )
    mobile: Optional[Annotated[
        str,
        StringConstraints(min_length=10, max_length=15)
    ]] = Field(
        None,
        example="9876543210",
        description="Updated mobile number of the user (optional, 10-15 digits)."
    )
    role: Optional[int] = Field(
        None,
        example=UserRole.USER.value,
        description="Role of the user (optional, mapped to a predefined set of roles)."
    )
    is_active: Optional[bool] = Field(
        None,
        example=True,
        description="Indicates if the user is currently active (optional)."
    )
    is_blocked: Optional[bool] = Field(
        None,
        example=False,
        description="Indicates if the user is blocked (optional)."
    )


# User Response (Output for API Responses)
class UserResponse(UserBase):
    id: int = Field(
        ...,
        example=1,
        description="Unique identifier for the user."
    )
    is_active: bool = Field(
        default=True,
        example=True,
        description="Indicates if the user is currently active."
    )
    is_blocked: bool = Field(
        default=False,
        example=False,
        description="Indicates if the user is blocked."
    )
    role: int = Field(
        default=UserRole.USER.value,
        example=UserRole.USER.value,
        description="Role of the user (mapped to a predefined set of roles)."
    )
    created_at: datetime = Field(
        ...,
        example="2025-01-25T12:00:00Z",
        description="Timestamp when the user was created."
    )
    updated_at: Optional[datetime] = Field(
        None,
        example="2025-01-26T12:00:00Z",
        description="Timestamp when the user was last updated (optional)."
    )

    class Config:
        from_attributes = True


# Login Request (Input for Authentication)
class UserLogin(BaseModel):
    email: EmailStr = Field(
        ...,
        example="user@example.com",
        description="Email address of the user for authentication."
    )
    password: Annotated[
        str,
        StringConstraints(min_length=8, max_length=64)
    ] = Field(
        ...,
        example="securepassword",
        description="Password of the user for authentication."
    )


# Token Data (Stored in Access Tokens)
class TokenData(BaseModel):
    sub: Optional[str] = Field(
        None,
        example="john_doe",
        description="Subject or username of the user."
    )
    user_id: Optional[int] = Field(
        None,
        example=1,
        description="Unique identifier of the user."
    )
    role: Optional[int] = Field(
        None,
        example=UserRole.USER.value,
        description="Role of the user (stored in the token)."
    )


# Access Token Response (Output for Token API)
class TokenResponse(BaseModel):
    access_token: Annotated[
        str,
        StringConstraints(min_length=20, max_length=500)
    ] = Field(
        ...,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        description="JWT access token for the user."
    )
    token_type: str = Field(
        ...,
        example="Bearer",
        description="Type of the token, typically 'Bearer'."
    )
