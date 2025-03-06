from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.enums import FeatureDataType, SubscriptionPlans


# SubscriptionPlan Models
class SubscriptionPlanCreate(BaseModel):
    name: SubscriptionPlans = Field(..., description="Name of the subscription plan")
    amount: float = Field(..., description="Cost of the subscription plan in USD")
    description: str = Field(
        ..., description="Detailed description of the plan features and benefits"
    )
    popular: bool = Field(
        default=False, description="Indicates if the plan is frequently chosen by users"
    )
    premium: bool = Field(
        default=False, description="Indicates if the plan offers premium features"
    )


class SubscriptionPlanUpdate(BaseModel):
    name: Optional[SubscriptionPlans] = Field(
        None, description="Updated name of the subscription plan"
    )
    amount: Optional[float] = Field(
        None, description="Updated cost of the subscription plan in USD"
    )
    description: Optional[str] = Field(
        None, description="Updated detailed description of the plan"
    )
    popular: Optional[bool] = Field(
        None, description="Updated indication if the plan is popular"
    )
    premium: Optional[bool] = Field(
        None, description="Updated indication if the plan offers premium features"
    )


class SubscriptionPlanResponse(SubscriptionPlanCreate):
    id: int = Field(..., description="Unique identifier for the subscription plan")
    created_at: datetime = Field(
        ..., description="Timestamp when the subscription plan was created"
    )
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp when the subscription plan was last updated"
    )

    class Config:
        from_attributes = True


# FeatureGroup Models
class FeatureGroupCreate(BaseModel):
    subscription_plan_id: int = Field(
        ..., description="Reference ID of the associated Subscription Plan"
    )
    title: str = Field(..., description="Title representing the feature group category")
    description: Optional[str] = Field(
        None, description="Detailed description of the feature group"
    )


class FeatureGroupUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Updated title of the feature group")
    description: Optional[str] = Field(
        None, description="Updated description of the feature group"
    )


class FeatureGroupResponse(FeatureGroupCreate):
    id: int = Field(..., description="Unique identifier for the feature group")
    created_at: datetime = Field(
        ..., description="Timestamp when the feature group was created"
    )
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp when the feature group was last updated"
    )

    class Config:
        from_attributes = True


# Features Models
class FeatureCreate(BaseModel):
    feature_group_id: int = Field(
        ..., description="Reference ID of the associated Feature Group"
    )
    key: str = Field(
        ...,
        description="Unique key identifier for the feature (e.g., 'storage', 'daily_limit')",
    )
    data_type: FeatureDataType = Field(
        ...,
        description="Specifies the data type of the feature value (e.g., STRING, NUMBER, BOOLEAN)",
    )
    required: bool = Field(
        default=False,
        description="Indicates if this feature is mandatory for the feature group",
    )
    value: Optional[str] = Field(
        None, description="Default value of the feature, if applicable"
    )
    numeric_value: Optional[int] = Field(
        None, description="Numeric value of the feature, if applicable"
    )


class FeatureUpdate(BaseModel):
    key: Optional[str] = Field(
        None, description="Updated key identifier for the feature"
    )
    data_type: Optional[FeatureDataType] = Field(
        None, description="Updated data type of the feature value"
    )
    required: Optional[bool] = Field(
        None, description="Updated indication if the feature is required"
    )
    value: Optional[str] = Field(
        None, description="Updated default value of the feature, if applicable"
    )
    numeric_value: Optional[int] = Field(
        None, description="Updated numeric value of the feature, if applicable"
    )


class FeatureResponse(FeatureCreate):
    id: int = Field(..., description="Unique identifier for the feature")
    created_at: datetime = Field(
        ..., description="Timestamp when the feature was created"
    )
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp when the feature was last updated"
    )

    class Config:
        from_attributes = True


# Feature Group with Features
class FeatureGroupWithFeatures(FeatureGroupResponse):
    features: List[Optional[FeatureResponse]] = Field(
        ..., description="List of features associated with this group."
    )

# Subscription Plan Details
class SubscriptionDetails(SubscriptionPlanResponse):
    feature_groups: List[Optional[FeatureGroupWithFeatures]] = Field(
        ..., description="List of feature groups associated with a plan."
    )