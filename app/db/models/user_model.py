from pydantic import ConfigDict
from sqlmodel import Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone

from app.db.database import Base
from app.schemas.user_schema import UserRole


class User(Base, table=True):
    """
    User schema representing system users.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "john_doe",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "mobile": "+1234567890",
                "password": "hashed_password",
                "role": 2,
                "is_active": True,
                "is_blocked": False,
                "created_at": "2025-01-01T12:00:00Z",
                "updated_at": "2025-01-02T15:30:00Z",
            }
        }
    )

    __tablename__ = "users"

    id: int = Field(
        default=None, primary_key=True, nullable=False,
        description="Unique identifier for the user.",
    )
    username: Optional[str] = Field(
        default=None, max_length=50, nullable=True, index=True,
        description="Unique username, optional.",
    )
    name: Optional[str] = Field(
        default=None, max_length=50, nullable=True, index=True,
        description="Full name of the user.",
    )
    email: str = Field(
        max_length=100, nullable=False, unique=True, index=True,
        description="User's email address (unique and required).",
    )
    mobile: Optional[str] = Field(
        default=None, max_length=15, nullable=True,
        description="User's mobile number, optional.",
    )
    password: str = Field(
        max_length=255, nullable=False,
        description="Hashed password for authentication.",
    )

    role: int = Field(
        default=UserRole.USER, nullable=False, 
        description="User role (e.g., Admin, Subadmin, User)."
    )
    is_active: bool = Field(
        default=True, nullable=False,
        description="Indicates if the user account is active.",
    )
    is_blocked: bool = Field(
        default=False, nullable=False,
        description="Indicates if the user is blocked from logging in.",
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
        description="Timestamp when the user was created.",
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=True,
        description="Timestamp when the user was last updated.",
    )

    # Relationships
    user_sessions: Optional[List["UserSession"]] = Relationship(back_populates="user")
