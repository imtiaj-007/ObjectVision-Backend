from sqlmodel import Field
from enum import Enum
from typing import Optional
from datetime import datetime, timezone
from app.db.database import Base


# User Role Enum
class UserRole(int, Enum):
    ADMIN = 1
    SUB_ADMIN = 2
    USER = 3


class User(Base, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, nullable=False, index=True)
    email: str = Field(max_length=100, nullable=False, unique=True, index=True)
    mobile: Optional[str] = Field(default=None, max_length=15)
    password: str = Field(max_length=255, nullable=False)
    role: int = Field(default=UserRole.USER.value, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    is_blocked: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    updated_at: Optional[datetime] = Field(default=None)