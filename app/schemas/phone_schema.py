from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from app.schemas.enums import ContactType


class PhoneNumberBase(BaseModel):
    """Base model for phone number validation."""

    phone_number: str = Field(
        ...,
        min_length=5,
        max_length=15,
        description="User's phone number (digits only)",
        example="1234567890",
    )
    country_code: str = Field(
        ...,
        min_length=2,
        max_length=5,
        description="Country code of the phone number (e.g., +91)",
        example="+91",
    )
    type: ContactType = Field(
        ...,
        description="Type of phone number (e.g., HOME, WORK)",
        example="HOME",
    )
    is_primary: bool = Field(
        default=False,
        description="Indicates if this is the primary phone number",
        example=True,
    )

    @field_validator("phone_number")
    def validate_phone_number(cls, value):
        """Validate that the phone number contains only digits."""
        if not value.isdigit():
            raise ValueError("Phone number must contain only digits")
        return value

    @field_validator("country_code")
    def validate_country_code(cls, value):
        """Validate that the country code starts with a '+' sign."""
        if not value.startswith("+"):
            raise ValueError("Country code must start with a '+' sign")
        return value


class PhoneNumberCreate(PhoneNumberBase):
    """Model for creating a new phone number record."""

    user_id: int = Field(
        ...,
        description="User ID associated with this phone number",
        example=10,
    )


class PhoneNumberUpdate(BaseModel):
    """Model for updating an existing phone number record."""
    
    type: Optional[ContactType] = Field(
        default=None,
        description="Type of phone number (e.g., HOME, WORK)",
        example="HOME",
    )
    is_primary: Optional[bool] = Field(
        default=None,
        description="Indicates if this is the primary phone number",
        example=True,
    )    

# For sending data to frontend
class PhoneNumberResponse(PhoneNumberBase):
    """Model for returning phone number records in API responses."""
    id: int = Field(..., description="Unique identifier for the phone number", example=1)
    created_at: datetime = Field(
        ...,
        description="Timestamp when the phone number was added",
        example="2025-02-15T10:00:00Z",
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the phone number was last updated",
        example="2025-02-15T10:07:00Z",
    )

    class Config:
        from_attributes = True

# For Internal use
class PhoneNumberData(PhoneNumberResponse):
    """Model for returning phone number records in API responses."""
    
    user_id: int = Field(
        ...,
        description="User ID associated with this phone number",
        example=10,
    )

    class Config:
        from_attributes = True