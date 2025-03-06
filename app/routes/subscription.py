from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import db_session_manager
from app.services.subscription_service import SubscriptionService, get_subscription_service
from app.schemas.subscription_schema import (
    SubscriptionPlanCreate, SubscriptionPlanUpdate, SubscriptionPlanResponse,
    FeatureGroupCreate, FeatureGroupUpdate, FeatureGroupResponse,
    FeatureCreate, FeatureUpdate, FeatureResponse,
    SubscriptionDetails
)

router = APIRouter()


# Subscription Plan routes
@router.post(
    "/plans",
    response_model=SubscriptionPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_subscription_plan(
    plan_data: SubscriptionPlanCreate,
    service: SubscriptionService = Depends(get_subscription_service),
):
    """Create a new subscription plan"""
    try:
        result = await service.create_subscription_plan(plan_data.dict())
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription plan: {str(e)}",
        )


@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def get_all_subscription_plans(
    service: SubscriptionService = Depends(get_subscription_service),
):
    """Get all subscription plans"""
    try:
        return await service.get_all_subscription_plans()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch subscription plans: {str(e)}",
        )


@router.get(
    "/plans/details",
    response_model=Union[List[SubscriptionDetails], SubscriptionDetails],
)
async def get_subscription_plan_with_features(
    plan_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(db_session_manager.get_db)
):
    """Get a subscription plan(s) with all its feature groups and features"""
    try:
        plan = await SubscriptionService.get_subscription_plan_with_features(db, plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscription {f'plan with ID {plan_id}' if plan_id else 'plans'} not found",
            )
        return plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch subscription plan details: {str(e)}",
        )


@router.get("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def get_subscription_plan(
    plan_id: int, service: SubscriptionService = Depends(get_subscription_service)
):
    """Get a subscription plan by ID"""
    try:
        plan = await service.get_subscription_plan(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscription plan with ID {plan_id} not found",
            )
        return plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch subscription plan: {str(e)}",
        )


@router.get("/plans/name/{name}", response_model=SubscriptionPlanResponse)
async def get_subscription_plan_by_name(
    name: str, service: SubscriptionService = Depends(get_subscription_service)
):
    """Get a subscription plan by name"""
    try:
        plan = await service.get_subscription_plan_by_name(name)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscription plan with name {name} not found",
            )
        return plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch subscription plan: {str(e)}",
        )


@router.put("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def update_subscription_plan(
    plan_id: int,
    plan_data: SubscriptionPlanUpdate,
    service: SubscriptionService = Depends(get_subscription_service),
):
    """Update a subscription plan"""
    try:
        # First check if plan exists
        plan = await service.get_subscription_plan(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscription plan with ID {plan_id} not found",
            )

        # Update plan
        update_data = {k: v for k, v in plan_data.dict().items() if v is not None}
        success = await service.update_subscription_plan(plan_id, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update subscription plan",
            )

        # Return updated plan
        return await service.get_subscription_plan(plan_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update subscription plan: {str(e)}",
        )


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription_plan(
    plan_id: int, service: SubscriptionService = Depends(get_subscription_service)
):
    """Delete a subscription plan"""
    try:
        success = await service.delete_subscription_plan(plan_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscription plan with ID {plan_id} not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete subscription plan: {str(e)}",
        )


# Feature Group routes
@router.get("/feature-groups", response_model=List[FeatureGroupResponse])
async def get_all_feature_groups(
    service: SubscriptionService = Depends(get_subscription_service),
):
    """Get all feature groups"""
    try:
        return await service.get_all_feature_groups()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch feature groups: {str(e)}",
        )


@router.get("/feature-groups/{group_id}", response_model=FeatureGroupResponse)
async def get_feature_group(
    group_id: int, service: SubscriptionService = Depends(get_subscription_service)
):
    """Get a feature group by ID"""
    try:
        group = await service.get_feature_group(group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature group with ID {group_id} not found",
            )
        return group
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch feature group: {str(e)}",
        )


@router.get(
    "/plans/{plan_id}/feature-groups", response_model=List[FeatureGroupResponse]
)
async def get_feature_groups_by_plan(
    plan_id: int, service: SubscriptionService = Depends(get_subscription_service)
):
    """Get feature groups by plan ID"""
    try:
        # Check if plan exists
        plan = await service.get_subscription_plan(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscription plan with ID {plan_id} not found",
            )

        return await service.get_feature_groups_by_plan(plan_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch feature groups: {str(e)}",
        )


@router.post(
    "/feature-groups",
    response_model=FeatureGroupResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_feature_group(
    group_data: FeatureGroupCreate,
    service: SubscriptionService = Depends(get_subscription_service),
):
    """Create a new feature group"""
    try:
        result = await service.create_feature_group(group_data.dict())
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create feature group: {str(e)}",
        )


@router.put("/feature-groups/{group_id}", response_model=FeatureGroupResponse)
async def update_feature_group(
    group_id: int,
    group_data: FeatureGroupUpdate,
    service: SubscriptionService = Depends(get_subscription_service),
):
    """Update a feature group"""
    try:
        # First check if group exists
        group = await service.get_feature_group(group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature group with ID {group_id} not found",
            )

        # Update group
        update_data = {k: v for k, v in group_data.dict().items() if v is not None}
        success = await service.update_feature_group(group_id, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update feature group",
            )

        # Return updated group
        return await service.get_feature_group(group_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update feature group: {str(e)}",
        )


@router.delete("/feature-groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feature_group(
    group_id: int, service: SubscriptionService = Depends(get_subscription_service)
):
    """Delete a feature group"""
    try:
        success = await service.delete_feature_group(group_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature group with ID {group_id} not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete feature group: {str(e)}",
        )


# Features routes
@router.get("/feature-groups/{group_id}/features", response_model=List[FeatureResponse])
async def get_features_by_group(
    group_id: int, service: SubscriptionService = Depends(get_subscription_service)
):
    """Get features by group ID"""
    try:
        return await service.get_features_by_group(group_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch features: {str(e)}",
        )


@router.get("/features/{feature_id}", response_model=FeatureResponse)
async def get_feature(
    feature_id: int, service: SubscriptionService = Depends(get_subscription_service)
):
    """Get a feature by ID"""
    try:
        feature = await service.get_feature(feature_id)
        if not feature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature with ID {feature_id} not found",
            )
        return feature
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch feature: {str(e)}",
        )


@router.post(
    "/features", response_model=FeatureResponse, status_code=status.HTTP_201_CREATED
)
async def create_feature(
    feature_data: FeatureCreate,
    service: SubscriptionService = Depends(get_subscription_service),
):
    """Create a new feature"""
    try:
        result = await service.create_feature(feature_data.dict())
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create feature: {str(e)}",
        )


@router.put("/features/{feature_id}", response_model=FeatureResponse)
async def update_feature(
    feature_id: int,
    feature_data: FeatureUpdate,
    service: SubscriptionService = Depends(get_subscription_service),
):
    """Update a feature"""
    try:
        # First check if feature exists
        feature = await service.get_feature(feature_id)
        if not feature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature with ID {feature_id} not found",
            )

        # Update feature
        update_data = {k: v for k, v in feature_data.dict().items() if v is not None}
        success = await service.update_feature(feature_id, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update feature",
            )
        return await service.get_feature(feature_id)
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update feature: {str(e)}",
        )


@router.delete("/features/{feature_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feature(
    feature_id: int, service: SubscriptionService = Depends(get_subscription_service)
):
    """Delete a feature"""
    try:
        success = await service.delete_feature(feature_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature with ID {feature_id} not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete feature: {str(e)}",
        )
