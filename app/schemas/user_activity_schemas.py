from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.schemas.enums import SubscriptionPlans, ActivityTypeEnum


# ---------------- ActiveUserPlans CRUD Models ----------------
class ActiveUserPlanBase(BaseModel):
    user_id: int = Field(..., description="User identifier")
    plan_id: int = Field(..., description="Subscription plan ID")
    plan_name: SubscriptionPlans = Field(..., description="Subscription plan name")
    description: Optional[str] = Field(None, description="Plan description")
    is_active: bool = Field(False, description="Indicates if the plan is active")
    expiry_date: Optional[datetime] = Field(
        None, description="Expiration date of the plan"
    )
    backup_till: Optional[datetime] = Field(None, description="Backup retention period")


class ActiveUserPlanCreate(ActiveUserPlanBase):
    pass


class ActiveUserPlanUpdate(BaseModel):
    plan_id: Optional[int] = None
    plan_name: Optional[SubscriptionPlans] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    expiry_date: Optional[datetime] = None
    backup_till: Optional[datetime] = None


class ActiveUserPlanResponse(ActiveUserPlanBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------------- UserActivity CRUD Models ----------------
class UserActivityBase(BaseModel):
    active_user_plan_id: int = Field(
        ..., description="Reference to the active user plan"
    )
    activity_type: ActivityTypeEnum = Field(
        ..., description="Type of user activity"
    )
    daily_usage: Optional[int] = Field(0, description="Amount of resource used per day")
    total_usage: Optional[int] = Field(0, description="Amount of resource used")
    daily_limit: Optional[int] = Field(None, description="Maximum allowed usage limit per day")
    total_limit: Optional[int] = Field(None, description="Maximum allowed usage limit")
    max_size: Optional[int] = Field(None, description="Max specified sizes of the entities")

class UserActivityCreate(UserActivityBase):
    pass

class UserActivityUpdate(BaseModel):
    activity_type: Optional[ActivityTypeEnum] = None
    daily_usage: Optional[int] = None
    total_usage: Optional[int] = None
    daily_limit: Optional[int] = None
    total_limit: Optional[int] = None
    max_size: Optional[int] = None

class UserActivityResponse(UserActivityBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True