from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from app.schemas.enums import ContactType


class AddressBase(BaseModel):
    """Base model for address validation."""

    address_line_1: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Primary address line",
        example="Apt 4B",
    )
    address_line_2: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Secondary address line (optional)",
        example="123 Main St",
    )
    city: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="City name",
        example="Kolkata",
    )
    state_province: Optional[str] = Field(
        default=None,
        max_length=100,
        description="State or Province name",
        example="WB",
    )
    postal_code: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Postal or ZIP code",
        example="700000",
    )
    country: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Full country name",
        example="India",
    )
    country_code: str = Field(
        ...,
        min_length=2,
        max_length=2,
        description="ISO country code (e.g., IN, US)",
        example="IN",
    )
    latitude: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90,
        description="Latitude of the address",
        example=40.7128,
    )
    longitude: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180,
        description="Longitude of the address",
        example=-74.0060,
    )
    type: ContactType = Field(
        ...,
        description="Type of address (e.g., HOME, WORK)",
        example="HOME",
    )

    @field_validator("country_code")
    def validate_country_code(cls, value):
        """Validate that the country code is a valid ISO 3166-1 alpha-2 code."""
        if len(value) != 2 or not value.isalpha():
            raise ValueError("Country code must be a 2-letter ISO code (e.g., IN, US)")
        return value.upper()
    

class AddressCreate(AddressBase):
    """Model for creating a new address record."""

    user_id: int = Field(
        ...,
        description="User ID associated with this address",
        example=10,
    )


class AddressUpdate(BaseModel):
    """Model for updating an existing address record."""

    address_line_1: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Primary address line",
        example="Apt 4B",
    )
    address_line_2: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Secondary address line (optional)",
        example="123 Main St",
    )    
    type: Optional[ContactType] = Field(
        default=None,
        description="Type of address (e.g., HOME, WORK)",
        example="HOME",
    )


# For sending data to frontend
class AddressResponse(AddressBase):
    """Model for returning address records in API responses."""

    id: int = Field(..., description="Unique identifier for the address", example=1)
    created_at: datetime = Field(
        ...,
        description="Timestamp when the address was added",
        example="2025-02-15T10:00:00Z",
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the address was last updated",
        example="2025-02-15T10:07:00Z",
    )

    class Config:
        from_attributes = True


# For Internal use
class AddressData(AddressResponse):
    """Model for returning address records in API responses."""
    
    user_id: int = Field(
        ...,
        description="User ID associated with this address",
        example=10,
    )

    class Config:
        from_attributes = True