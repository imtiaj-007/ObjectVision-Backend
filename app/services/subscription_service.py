from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.subscription import SubscriptionPlan, Features, FeatureGroup
from app.repository.subscription_repository import SubscriptionRepository
from app.utils.logger import log


async def get_subscription_service():
    pass

class SubscriptionService:
    """
    Service class for handling business logic related to subscriptions.
    Uses the SubscriptionRepository for database operations.
    """

    # Subscription Plan service methods
    async def create_subscription_plan(
        db: AsyncSession, subscription_data: Dict[str, Any]
    ) -> SubscriptionPlan:
        """Create a new subscription plan with validation."""
        try:
            # Check if a plan with the same name already exists
            existing_plan = (
                await SubscriptionRepository.get_subscription_plan_by_name(
                    db, subscription_data.get("name")
                )
            )
            if existing_plan:
                raise ValueError(
                    f"Subscription plan with name '{subscription_data.get('name')}' already exists"
                )

            return await SubscriptionRepository.create_subscription_plan(
                subscription_data
            )

        except Exception as e:
            log.error(f"Error in create_subscription_plan service: {e}")
            raise


    async def get_subscription_plan(db: AsyncSession, plan_id: int) -> Optional[SubscriptionPlan]:
        """Get subscription plan by ID."""
        try:
            return await SubscriptionRepository.get_subscription_plan_by_id(
                db, plan_id
            )
        except Exception as e:
            log.error(f"Error in get_subscription_plan service: {e}")
            raise


    async def get_subscription_plan_by_name(
        self, name: str
    ) -> Optional[SubscriptionPlan]:
        """Get subscription plan by name."""
        try:
            return await self.subscription_repository.get_subscription_plan_by_name(
                name
            )
        except Exception as e:
            log.error(f"Error in get_subscription_plan_by_name service: {e}")
            raise


    async def get_all_subscription_plans(self) -> List[SubscriptionPlan]:
        """Get all subscription plans."""
        try:
            return await self.subscription_repository.get_all_subscription_plans()
        except Exception as e:
            log.error(f"Error in get_all_subscription_plans service: {e}")
            raise


    async def update_subscription_plan(
        self, plan_id: int, update_data: Dict[str, Any]
    ) -> bool:
        """Update a subscription plan with validation."""
        try:
            # Check if plan exists
            existing_plan = (
                await self.subscription_repository.get_subscription_plan_by_id(plan_id)
            )
            if not existing_plan:
                raise ValueError(f"Subscription plan with ID {plan_id} does not exist")

            # If name is being changed, ensure the new name doesn't conflict
            if "name" in update_data and update_data["name"] != existing_plan.name:
                name_check = (
                    await self.subscription_repository.get_subscription_plan_by_name(
                        update_data["name"]
                    )
                )
                if name_check:
                    raise ValueError(
                        f"Subscription plan with name '{update_data['name']}' already exists"
                    )

            return await self.subscription_repository.update_subscription_plan(
                plan_id, update_data
            )
        except Exception as e:
            log.error(f"Error in update_subscription_plan service: {e}")
            raise


    async def delete_subscription_plan(self, plan_id: int) -> bool:
        """Delete a subscription plan."""
        try:
            return await self.subscription_repository.delete_subscription_plan(plan_id)
        except Exception as e:
            log.error(f"Error in delete_subscription_plan service: {e}")
            raise


    async def get_subscription_plan_with_features(
        db: AsyncSession, plan_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get subscription plan(s) with feature groups and features.
        If plan_id is provided, return details for that specific plan.
        If plan_id is not provided, return a list of all plans with details.
        """
        try:
            data = await SubscriptionRepository.get_subscription_plan_details(
                db, plan_id
            )
            if not data:
                return None if plan_id is not None else []

            # Add features to each feature group
            if plan_id is not None:
                # Single plan case
                plan_dict = data.model_dump()
                plan_dict["feature_groups"] = [
                    {
                        **group.model_dump(),
                        "features": [feature.model_dump() for feature in group.features]
                    }
                    for group in data.feature_group
                ]
                return plan_dict
            else:
                # Multiple plans case
                return [
                    {
                        **plan.model_dump(),
                        "feature_groups": [
                            {
                                **group.model_dump(),
                                "features": [feature.model_dump() for feature in group.features]
                            }
                            for group in plan.feature_group
                        ]
                    }
                    for plan in data
                ]

        except Exception as e:
            log.error(f"Error in get_subscription_plan_with_features service: {e}")
            raise


    # Feature Group service methods
    async def get_all_feature_groups(self) -> List[FeatureGroup]:
        """Get all feature groups."""
        try:
            return await self.subscription_repository.get_all_feature_groups()
        except Exception as e:
            log.error(f"Error in get_all_feature_groups service: {e}")
            raise


    async def get_feature_group(self, group_id: int) -> Optional[FeatureGroup]:
        """Get feature group by ID."""
        try:
            return await self.subscription_repository.get_feature_group_by_id(group_id)
        except Exception as e:
            log.error(f"Error in get_feature_group service: {e}")
            raise


    async def get_feature_groups_by_plan(self, plan_id: int) -> List[FeatureGroup]:
        """Get feature groups by plan ID."""
        try:
            return await self.subscription_repository.get_feature_groups_by_plan_id(
                plan_id
            )
        except Exception as e:
            log.error(f"Error in get_feature_groups_by_plan service: {e}")
            raise


    async def create_feature_group(self, group_data: Dict[str, Any]) -> FeatureGroup:
        """Create a new feature group with validation."""
        try:
            # Verify the subscription plan exists
            plan_id = group_data.get("subscription_plan_id")
            if plan_id:
                plan = await self.subscription_repository.get_subscription_plan_by_id(
                    plan_id
                )
                if not plan:
                    raise ValueError(
                        f"Subscription plan with ID {plan_id} does not exist"
                    )

            return await self.subscription_repository.create_feature_group(group_data)
        except Exception as e:
            log.error(f"Error in create_feature_group service: {e}")
            raise


    async def update_feature_group(
        self, group_id: int, update_data: Dict[str, Any]
    ) -> bool:
        """Update a feature group with validation."""
        try:
            # Check if group exists
            existing_group = await self.subscription_repository.get_feature_group_by_id(
                group_id
            )
            if not existing_group:
                raise ValueError(f"Feature group with ID {group_id} does not exist")

            # If subscription_plan_id is being changed, verify the new plan exists
            if (
                "subscription_plan_id" in update_data
                and update_data["subscription_plan_id"]
                != existing_group.subscription_plan_id
            ):
                plan = await self.subscription_repository.get_subscription_plan_by_id(
                    update_data["subscription_plan_id"]
                )
                if not plan:
                    raise ValueError(
                        f"Subscription plan with ID {update_data['subscription_plan_id']} does not exist"
                    )

            return await self.subscription_repository.update_feature_group(
                group_id, update_data
            )
        except Exception as e:
            log.error(f"Error in update_feature_group service: {e}")
            raise


    async def delete_feature_group(self, group_id: int) -> bool:
        """Delete a feature group."""
        try:
            return await self.subscription_repository.delete_feature_group(group_id)
        except Exception as e:
            log.error(f"Error in delete_feature_group service: {e}")
            raise


    # Features service methods
    async def get_features_by_group(self, group_id: int) -> List[Features]:
        """Get features by group ID."""
        try:
            # Verify group exists
            group = await self.subscription_repository.get_feature_group_by_id(group_id)
            if not group:
                raise ValueError(f"Feature group with ID {group_id} does not exist")

            return await self.subscription_repository.get_features_by_group_id(group_id)
        except Exception as e:
            log.error(f"Error in get_features_by_group service: {e}")
            raise


    async def get_feature(self, feature_id: int) -> Optional[Features]:
        """Get feature by ID."""
        try:
            return await self.subscription_repository.get_feature_by_id(feature_id)
        except Exception as e:
            log.error(f"Error in get_feature service: {e}")
            raise


    async def create_feature(self, feature_data: Dict[str, Any]) -> Features:
        """Create a new feature with validation."""
        try:
            # Verify the feature group exists
            group_id = feature_data.get("feature_group_id")
            if group_id:
                group = await self.subscription_repository.get_feature_group_by_id(
                    group_id
                )
                if not group:
                    raise ValueError(f"Feature group with ID {group_id} does not exist")

            return await self.subscription_repository.create_feature(feature_data)
        except Exception as e:
            log.error(f"Error in create_feature service: {e}")
            raise


    async def update_feature(
        self, feature_id: int, update_data: Dict[str, Any]
    ) -> bool:
        """Update a feature with validation."""
        try:
            # Check if feature exists
            existing_feature = await self.subscription_repository.get_feature_by_id(
                feature_id
            )
            if not existing_feature:
                raise ValueError(f"Feature with ID {feature_id} does not exist")

            # If feature_group_id is being changed, verify the new group exists
            if (
                "feature_group_id" in update_data
                and update_data["feature_group_id"] != existing_feature.feature_group_id
            ):
                group = await self.subscription_repository.get_feature_group_by_id(
                    update_data["feature_group_id"]
                )
                if not group:
                    raise ValueError(
                        f"Feature group with ID {update_data['feature_group_id']} does not exist"
                    )

            return await self.subscription_repository.update_feature(
                feature_id, update_data
            )
        except Exception as e:
            log.error(f"Error in update_feature service: {e}")
            raise


    async def delete_feature(self, feature_id: int) -> bool:
        """Delete a feature."""
        try:
            return await self.subscription_repository.delete_feature(feature_id)
        except Exception as e:
            log.error(f"Error in delete_feature service: {e}")
            raise
