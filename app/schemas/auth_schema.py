from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, EmailStr


class ResponseTypes(int, Enum):
    FAILED = 0
    SUCCESS = 1


# General response format
class GeneralResponse(BaseModel):
    status: ResponseTypes = Field(
        ...,
        example=ResponseTypes.SUCCESS,
        description="Status indicating response type"
    )
    message: str = Field(
        ...,
        example="User registration successful",
        description="Message of the general response"
    )
    

# Refresh Token Format
class SignupResponse(GeneralResponse):
    user_id: int = Field(
        ...,
        example=1,
        description="Unique identifier for the user."
    )
    email: EmailStr = Field(
        ...,
        example="user@example.com",
        description="Valid email address of the user."
    )