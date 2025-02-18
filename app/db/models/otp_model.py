from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy import DateTime
from datetime import datetime, timezone
from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.user_model import User


class OTP(Base, table=True):
    __tablename__ = "otps"
    __table_args__ = {
        'schema': None,
        'keep_existing': True
    }

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)
    email: str = Field(
        index=True,
        max_length=255,
        nullable=False,
        description="Email address associated with the OTP",
    )
    type: str = Field(
        default="email_verification",
        max_length=30,
        description="Purpose of the OTP (email_verification, password_reset, etc.)",
    )
    otp: str = Field(
        min_length=6,
        max_length=10,
        nullable=False,
        description="6-digit OTP or alphanumeric token",
    )
    is_used: bool = Field(
        default=False, description="Whether the OTP has been used"
    )
    attempt_count: int = Field(
        default=0, description="Number of verification attempts"
    )
    expires_at: datetime = Field(
        index=True, sa_type=DateTime(timezone=True), nullable=False, description="When the OTP expires"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        description="When the OTP was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        description="When the OTP was last updated",
    )

    # Relationships
    user: Optional["User"] = Relationship(back_populates="otps")
    
