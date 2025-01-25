from typing import Optional
from pydantic import BaseModel, EmailStr, Field, StringConstraints
from typing_extensions import Annotated
from datetime import datetime
from app.db.schemas.user_schema import UserRole


# Base User Model (Shared Fields)
class UserBase(BaseModel):
    username: Annotated[str, StringConstraints(min_length=3, max_length=50)] = Field(
        example="john_doe"
    )
    email: EmailStr = Field(example="user@example.com")
    mobile: Optional[str] = Field(None, example="1234567890")        

    class Config:
        from_attributes = True


# Create User (Input for Creating Users)
class UserCreate(UserBase):    
    password: Annotated[
        str,
        StringConstraints(min_length=8, max_length=64),
    ] = Field(example="securepassword")


# Update User (Input for Updating Users)
class UserUpdate(BaseModel):
    username: Optional[
        Annotated[
            str,
            StringConstraints(min_length=3, max_length=50),
        ]
    ] = Field(None, example="new_username")
    email: Optional[EmailStr] = Field(None, example="new_email@example.com")
    mobile: Optional[str] = Field(None, example="9876543210")
    role: Optional[int] = Field(None, example=UserRole.USER.value)
    is_active: Optional[bool] = Field(None, example=False)
    is_blocked: Optional[bool] = Field(None, example=True)


# User Response (Output for API Responses)
class UserResponse(UserBase):
    is_active: bool = Field(default=True, example=True)
    is_blocked: bool = Field(default=False, example=False)
    role: int = Field(default=UserRole.USER.value, example=UserRole.USER.value)

    class Config:
        from_attributes = True


# Login Request (Input for Authentication)
class UserLogin(BaseModel):
    email: EmailStr = Field(example="user@example.com")
    password: str = Field(min_length=8, max_length=64, example="securepassword")


# Token Data (Stored in Access Tokens)
class TokenData(BaseModel):
    sub: str = Field(None, example="john_doe")
    user_id: int = Field(None, example=1)
    role: int = Field(None, example=UserRole.USER.value)


# Access Token Response
class TokenResponse(BaseModel):
    access_token: str = Field(example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(example="Bearer")
