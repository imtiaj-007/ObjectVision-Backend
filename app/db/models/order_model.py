from pydantic import ConfigDict
from sqlmodel import Field, DateTime, Relationship
from decimal import Decimal
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from app.schemas.enums import CurrencyEnum, SubscriptionPlans, PaymentStatus
from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.user_model import User
    from app.db.models.subscription import SubscriptionPlan


class Order(Base, table=True):
    """
    Defines individual features with their configurations.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 23,
                "plan_id": 3,
                "razorpay_order_id": "rpay_abcXYZ",
                "receipt": "receipt_29654873145",
                "plan_name": "GOLD",
                "amount": 100,
                "currency": "INR",
                "status": "created",
                "description": "Monthly subscription",
                "promo_code": "WELCOME10",
                "created_at": "2025-02-15T10:00:00Z",
                "updated_at": "2025-02-15T10:07:00Z",
            }
        },
    )

    __tablename__ = "orders"
    __table_args__ = {"schema": None, "keep_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        foreign_key="users.id",
        ondelete="CASCADE",
        index=True,
        description="Customer identifier",
    )
    plan_id: int = Field(
        foreign_key="subscription_plan.id",
        ondelete="SET NULL",
        index=True,
        nullable=True,
        description="Subscription plan ID / top-up ID",
    )
    razorpay_order_id: str = Field(index=True, unique=True, description="Razorpay order ID")
    receipt: str = Field(
        default=f"receipt_{datetime.now()}",
        description="Unique order identifier [server generated]",
    )
    plan_name: SubscriptionPlans = Field(
        index=True,
        description="plan name of the order entity [subscription name / top-up name]",
    )
    amount: Decimal = Field(
        ..., gt=0, description="Amount to be paid, must be greater than 0"
    )
    currency: CurrencyEnum = Field(
        default=CurrencyEnum.INR, description="Currency of the payment"
    )
    status: PaymentStatus = Field(
        default=PaymentStatus.CREATED,
        index=True,
        nullable=False,
        description="Current status of the payment.",
    )
    description: Optional[str] = Field(default=None, description="Payment description")
    promo_code: Optional[str] = Field(
        default=None, description="Promo code for discounts"
    )
    created_at: datetime = Field(
        index=True,
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
        description="Timestamp when the order was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=True,
        description="Timestamp when the order was last updated",
    )

    # Relationships
    user: "User" = Relationship(back_populates="orders")  # Many-to-One Relationship (Orders → User)
    subscription_plan: "SubscriptionPlan" = Relationship(back_populates="order")  # One-to-One Relationship (Order → SubscriptionPlan)
