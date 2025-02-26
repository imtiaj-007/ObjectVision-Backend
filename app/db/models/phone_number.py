from pydantic import ConfigDict
from sqlalchemy import DateTime, UniqueConstraint, Index
from sqlmodel import Field, Relationship
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from app.db.database import Base
from app.schemas.enums import ContactType

if TYPE_CHECKING:
    from app.db.models.user_model import User


class PhoneNumber(Base, table=True):
    """Stores phone numbers of users."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 10,
                "phone_number": "1234567890",
                "country_code": "+91",
                "type": "HOME",
                "is_primary": True,
                "created_at": "2025-02-15T10:00:00Z",
                "updated_at": "2025-02-15T10:07:00Z",
            }
        },
    )

    __tablename__ = "phone_numbers"
    __table_args__ = (
        UniqueConstraint("user_id", "phone_number", name="uq_user_phone"),
        Index("ix_user_primary_phone", "user_id", unique=True, postgresql_where="is_primary = TRUE"),
        {
            "schema": None,
            "keep_existing": True,
        },
    )

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field( 
        foreign_key="users.id",
        index=True,
        nullable=False,
        description="User ID associated with this phone number",
    )
    phone_number: str = Field(
        nullable=False,
        min_length=10,
        max_length=15,  
        regex="^[0-9]+$",
        index=True,
        description="User's phone number (digits only)",
    )
    country_code: str = Field(
        nullable=False,
        max_length=5,  
        regex="^\+[0-9]{1,4}$",
        description="Country code of the phone number (e.g., +91)",
    )
    type: ContactType = Field(
        nullable=False,
        index=True,
        description="Type of phone number (e.g., HOME, WORK)",
    )
    is_primary: bool = Field(
        default=False, description="Indicates if this is the primary phone number"
    )
    is_verified: bool = Field(
        default=False,
        description="Whether this phone number has been verified"
    )
    verified_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        description="Timestamp when the phone number was verified"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
        description="Timestamp when the phone number was added",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=True,
        description="Timestamp when the phone number was last updated",
    )

    # Relationships
    user: Optional["User"] = Relationship(
        back_populates="phone_numbers", sa_relationship_kwargs={"lazy": "joined"}
    )  # One-to-Many relationship (User → Phone Numbers)
