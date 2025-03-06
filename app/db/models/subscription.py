from pydantic import ConfigDict, field_validator
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship, DateTime, UniqueConstraint
from datetime import datetime, timezone
from app.db.database import Base
from app.schemas.enums import FeatureDataType, SubscriptionPlans

if TYPE_CHECKING:
    from app.db.models.order_model import Order
    from app.db.models.user_activity_model import ActiveUserPlans


class SubscriptionPlan(Base, table=True):
    """
    Stores available subscription plans.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 2,
                "name": "SILVER",
                "amount": 50,
                "description": "Ideal for regular users and moderate usage.",
                "popular": True,
                "premium": False,
                "created_at": "2025-02-15T10:00:00Z",
                "updated_at": "2025-02-15T10:07:00Z",
            }
        },
    )

    __tablename__ = "subscription_plan"
    __table_args__ = (
        UniqueConstraint("name", name="uq_subscription_plan_name"),
        {"schema": None, "keep_existing": True}
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    name: SubscriptionPlans = Field(
        index=True, unique=True, description="Name of the subscription plan"
    )
    amount: float = Field(description="Cost of the subscription plan")
    description: str = Field(description="Detailed description of the plan")
    popular: bool = Field(default=False, description="Indicates if the plan is popular")
    premium: bool = Field(
        default=False, description="Indicates if the plan is a premium plan"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
        description="Timestamp when the subscription_plan was added",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=True,
        description="Timestamp when the subscription_plan was last updated",
    )

    # Relationships
    feature_group: List["FeatureGroup"] = Relationship(back_populates="subscription_plan") 
    order: "Order" = Relationship(back_populates="subscription_plan")
    active_user_plans: "ActiveUserPlans" = Relationship(back_populates="subscription_plan")

    # Data validations for required fields
    @field_validator("amount")
    def validate_amount(cls, value):
        if value < 0:
            raise ValueError("Amount must be non-negative")
        return value


class FeatureGroup(Base, table=True):
    """
    Defines feature categories that can be assigned to subscription plans.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "subscription_plan_id": 4,
                "title": "Dashboard & Overview",
                "description": "Overview of the plan with key insights",
                "created_at": "2025-02-15T10:00:00Z",
                "updated_at": "2025-02-15T10:07:00Z",
            }
        },
    )

    __tablename__ = "feature_group"
    __table_args__ = {"schema": None, "keep_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    subscription_plan_id: int = Field(
        foreign_key="subscription_plan.id",
        ondelete="CASCADE",
        index=True,
        description="Link with a Subscription plan by plan_id"
    )
    title: str = Field(
        index=True,
        description="Feature type name (e.g., 'Dashboard & Overview', 'AI Model Access')",
    )
    description: Optional[str] = Field(
        default=None, description="Description of this feature type"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
        description="Timestamp when the feature_group was added",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=True,
        description="Timestamp when the feature_group was last updated",
    )

    # Relationship
    subscription_plan: "SubscriptionPlan" = Relationship(back_populates="feature_group")
    features: List["Features"] = Relationship(back_populates="feature_group")


class Features(Base, table=True):
    """
    Defines individual features with their configurations.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 4,
                "feature_group_id": 1,
                "key": "Validity",
                "data_type": "NUMBER",
                "required": True,
                "value": 15,
                "created_at": "2025-02-15T10:00:00Z",
                "updated_at": "2025-02-15T10:07:00Z",
            }
        },
    )

    __tablename__ = "features"
    __table_args__ = {"schema": None, "keep_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    feature_group_id: int = Field(
        foreign_key="feature_group.id",
        ondelete="CASCADE",
        index=True,
        description="Reference to the feature group",
    )
    key: str = Field(
        index=True, description="Feature property key (e.g., 'storage', 'daily_limit')"
    )
    data_type: FeatureDataType = Field(
        default=FeatureDataType.STRING,
        description="Data type of the feature value (string, number, boolean, etc.)",
    )
    required: bool = Field(
        default=False,
        description="Whether this feature is required for the feature type",
    )
    value: str = Field(
        description="Default value if not specified"
    )
    numeric_value: Optional[int] = Field(
        default=None, description="Numeric field to handle numeric values like storage, validity etc."
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
        description="Timestamp when the feature was added",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=True,
        description="Timestamp when the feature was last updated",
    )

    # Relationships
    feature_group: "FeatureGroup" = Relationship(back_populates="features")
