from pydantic import ConfigDict
from sqlmodel import Field, DateTime, Relationship
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from app.schemas.enums import SubscriptionPlans, ActivityTypeEnum
from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.user_model import User
    from app.db.models.subscription import SubscriptionPlan


class ActiveUserPlans(Base, table=True):
    """
    Defines individual features with their configurations.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 23,
                "plan_id": 3,
                "plan_name": "SILVER",
                "description": "Ideal for regular users and moderate usage.",
                "is_active": True,
                "expiry_date": "2025-03-17T10:00:00Z",
                "backup_till": "2025-04-14T10:00:00Z",
                "created_at": "2025-02-15T10:00:00Z",
                "updated_at": "2025-02-15T10:07:00Z",
            }
        },
    )

    __tablename__ = "active_user_plans"
    __table_args__ = {"schema": None, "keep_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        foreign_key="users.id",
        ondelete="SET NULL",
        index=True,
        nullable=True,
        description="Customer identifier",
    )
    plan_id: int = Field(
        foreign_key="subscription_plan.id",
        ondelete="SET NULL",
        index=True,
        nullable=True,
        description="Subscription plan ID / top-up ID",
    )
    plan_name: SubscriptionPlans = Field(
        index=True,
        description="plan name of the order entity [subscription name / top-up name]",
    )
    description: Optional[str] = Field(default=None, description="Payment description")
    is_active: bool = Field(
        default=False, description="Whether the purchased plan is currently active"
    )
    expiry_date: Optional[datetime] = Field(
        default=None, 
        sa_type=DateTime(timezone=True),
        description="Timestamp when the current plan expires"
    )
    backup_till: Optional[datetime] = Field(
        default=None, 
        sa_type=DateTime(timezone=True),
        description="Timestamp until which backups are available"
    )

    created_at: datetime = Field(
        index=True,
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
        description="Timestamp when the plan-mapping was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
        description="Timestamp when the plan-mapping was last updated",
    )

    # Relationships
    user: "User" = Relationship(back_populates="active_user_plans")  # Many-to-One Relationship (ActivePlans → User)
    subscription_plan: "SubscriptionPlan" = Relationship(back_populates="active_user_plans")  # One-to-One Relationship (ActivePlan → SubscriptionPlan)
    user_activities: List["UserActivity"] = Relationship(back_populates="active_user_plan")   # One-to-Many Relationship (ActivePlan → UserActivities)



class UserActivity(Base, table=True):
    """
    Defines individual features with their configurations.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "active_user_plan_id": 5,
                "activity_type": "IMAGE_USAGE",
                "daily_usage": 2,
                "total_usage": 8,
                "daily_limit": 5,
                "total_limit": 30,
                "max_size": 5,
                "created_at": "2025-02-15T10:00:00Z",
                "updated_at": "2025-02-15T10:07:00Z",
            }
        },
    )

    __tablename__ = "user_activity"
    __table_args__ = {"schema": None, "keep_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    active_user_plan_id: int = Field(
        foreign_key="active_user_plans.id",
        ondelete="CASCADE",
        index=True,
        description="Reference to the active user plan",
    )
    activity_type: ActivityTypeEnum = Field(
        index=True,
        description="Type of user activity (e.g., STORAGE_USAGE, IMAGE_USAGE)",
    )

    daily_usage: Optional[int] = Field(
        default=0,
        description="Amount of resource used per day",
    )
    total_usage: Optional[int] = Field(
        default=0,
        description="Amount of resource used",
    )

    daily_limit: Optional[int] = Field(
        default=None,
        description="Maximum allowed usage limit per day (if applicable)",
    )
    total_limit: Optional[int] = Field(
        default=None,
        description="Maximum allowed usage limit (if applicable)",
    )
    max_size: Optional[int] = Field(
        default=None, description="Max specified sizes of the entities (if applicable)"
    )

    created_at: datetime = Field(
        index=True,
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
        description="Timestamp when the activity was logged",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=True,
        description="Timestamp when the activity was last updated",
    )

    # Relationships
    active_user_plan: "ActiveUserPlans" = Relationship(back_populates="user_activities")  # Many-to-One Relationship (UserActivities → ActivePlan)
