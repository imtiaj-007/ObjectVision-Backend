from pydantic import ConfigDict
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from app.db.database import Base
from app.schemas.enums import ContactType

if TYPE_CHECKING:
    from app.db.models.user_model import User


class Address(Base, table=True):
    """Stores addresses of users."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 10,
                "address_line_1": "Apt 4B",
                "address_line_2": "123 Main St",
                "city": "New York",
                "state_province": "NY",
                "postal_code": "10001",
                "country": "United States",
                "country_code": "US",
                "latitude": "40.7128",
                "longitude": "-74.0060",
                "type": "HOME",
                "created_at": "2025-02-15T10:00:00Z",
                "updated_at": "2025-02-15T10:07:00Z",
            }
        },
    )

    __tablename__ = "addresses"
    __table_args__ = {
        "schema": None, 
        "keep_existing": True
    }

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(
        foreign_key="users.id",
        index=True,
        nullable=False,
        description="User ID associated with this address",
    )
    address_line_1: str = Field(nullable=False, description="Primary address line")
    address_line_2: Optional[str] = Field(
        default=None, description="Secondary address line (optional)"
    )
    city: str = Field(nullable=False, index=True, description="City name")
    state_province: str = Field(
        nullable=False, index=True, description="State or Province name"
    )
    postal_code: str = Field(nullable=False, description="Postal or ZIP code")
    country: str = Field(nullable=False, index=True, description="Full country name")
    country_code: str = Field(
        nullable=False,
        index=True,
        min_length=2,
        max_length=2,
        description="ISO 2-letter country code",
    )
    latitude: Optional[float] = Field(
        default=None, 
        ge=-90,
        le=90, 
        description="Latitude of the address"
    )
    longitude: Optional[float] = Field(
        default=None, 
        ge=-180,
        le=180,
        description="Longitude of the address"
    )
    type: ContactType = Field(
        nullable=False,
        index=True,
        description="Type of address (e.g., HOME, WORK)",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
        description="Timestamp when the address was added",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=True,
        description="Timestamp when the address was last updated",
    )

    # Relationships
    user: Optional["User"] = Relationship(
        back_populates="addresses", sa_relationship_kwargs={"lazy": "joined"}
    )  # One-to-Many relationship (User → Addresses)
