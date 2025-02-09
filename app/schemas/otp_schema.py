from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class OTPBase(BaseModel):
    email: EmailStr = Field(
        ...,
        max_length=255,
        description="Email address associated with the OTP"
    )
    type: str = Field(
        ...,
        max_length=20,
        description="Purpose of the OTP (email_verification, password_reset, etc.)"
    )
    otp: str = Field(
        ...,
        max_length=6,
        min_length=6,
        description="6-digit OTP value"
    )
    is_used: bool = Field(
        ...,
        description="Whether the OTP has been used"
    )
    attempt_count: int = Field(
        ...,
        description="Number of verification attempts"
    )
    expires_at: datetime = Field(
        ...,
        description="When the OTP expires"
    )

class OTPCreate(BaseModel):
    user_id: int = Field(
        ...,
        description="Unique id of a user"
    )

class OTPResend(BaseModel):
    user_id: int = Field(
        ...,
        description="Unique id of a user"
    )
    email: EmailStr = Field(
        ...,
        max_length=255,
        description="Email address associated with the OTP"
    )        

class OTPVerify(OTPResend):
    otp: str = Field(
        ...,
        max_length=6,
        min_length=6,
        description="6-digit OTP value"
    )
