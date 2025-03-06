from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlmodel import select, update
from sqlalchemy.orm import joinedload, aliased
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.subscription import SubscriptionPlan, Features, FeatureGroup
from app.utils.logger import log


class SubscriptionRepository:
    """
    Repository class for handling database operations related to subscriptions.
    """

    # Subscription Plan CRUD operations
    async def create_subscription_plan(
        db: AsyncSession, subscription_data: Dict[str, Any]
    ) -> SubscriptionPlan:
        """Create a new subscription plan"""
        try:
            subscription_plan = SubscriptionPlan(**subscription_data)
            db.add(subscription_plan)
            await db.commit()
            await db.refresh(subscription_plan)
            return subscription_plan

        except Exception as e:
            log.critical(f"Unexpected error in create_subscription_plan: {e}")
            raise

    async def get_subscription_plan_by_id(
        db: AsyncSession, plan_id: int
    ) -> Optional[SubscriptionPlan]:
        """Get subscription plan by ID"""
        try:
            statement = select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
            result = await db.execute(statement)
            return result.scalar_one_or_none()

        except Exception as e:
            log.critical(f"Unexpected error in get_subscription_plan_by_id: {e}")
            raise

    async def get_subscription_plan_by_name(
        self, name: str
    ) -> Optional[SubscriptionPlan]:
        """Get subscription plan by name"""
        try:
            statement = select(SubscriptionPlan).where(SubscriptionPlan.name == name)
            result = await self.session.execute(statement)
            return result.scalar_one_or_none()

        except Exception as e:
            log.critical(f"Unexpected error in get_subscription_plan_by_name: {e}")
            raise

    async def get_all_subscription_plans(self) -> List[SubscriptionPlan]:
        """Get all subscription plans"""
        try:
            statement = select(SubscriptionPlan)
            result = await self.session.execute(statement)
            return result.scalars().all()

        except Exception as e:
            log.critical(f"Unexpected error in get_all_subscription_plans: {e}")
            raise

    async def update_subscription_plan(
        self, plan_id: int, update_data: Dict[str, Any]
    ) -> bool:
        """Update a subscription plan"""
        try:
            statement = (
                update(SubscriptionPlan)
                .where(SubscriptionPlan.id == plan_id)
                .values(**update_data, updated_at=datetime.now(timezone.utc))
            )
            await self.session.execute(statement)
            await self.session.commit()
            return True

        except Exception as e:
            log.critical(f"Unexpected error in update_subscription_plan: {e}")
            raise

    async def delete_subscription_plan(self, plan_id: int) -> bool:
        """Delete a subscription plan"""
        try:
            subscription_plan = await self.get_subscription_plan_by_id(plan_id)
            if subscription_plan:
                await self.session.delete(subscription_plan)
                await self.session.commit()
                return True
            return False

        except Exception as e:
            log.critical(f"Unexpected error in delete_subscription_plan: {e}")
            raise

    # Feature Group CRUD operations
    async def get_all_feature_groups(self) -> List[FeatureGroup]:
        """Get all feature groups"""
        try:
            statement = select(FeatureGroup)
            result = await self.session.execute(statement)
            return result.scalars().all()

        except Exception as e:
            log.critical(f"Unexpected error in get_all_feature_groups: {e}")
            raise

    async def get_feature_group_by_id(self, group_id: int) -> Optional[FeatureGroup]:
        """Get feature group by ID"""
        try:
            statement = select(FeatureGroup).where(FeatureGroup.id == group_id)
            result = await self.session.execute(statement)
            return result.scalar_one_or_none()
        except Exception as e:
            log.critical(f"Unexpected error in get_feature_group_by_id: {e}")
            raise

    async def get_feature_groups_by_plan_id(
        self, plan_id: int
    ) -> Optional[List[FeatureGroup]]:
        """Get list of feature groups by plan ID"""
        try:
            statement = select(FeatureGroup).where(
                FeatureGroup.subscription_plan_id == plan_id
            )
            result = await self.session.execute(statement)
            return result.scalars().all()

        except Exception as e:
            log.critical(f"Unexpected error in get_feature_groups_by_plan_id: {e}")
            raise

    async def create_feature_group(self, group_data: Dict[str, Any]) -> FeatureGroup:
        """Create a new feature group"""
        try:
            feature_group = FeatureGroup(**group_data)
            self.session.add(feature_group)
            await self.session.commit()
            await self.session.refresh(feature_group)
            return feature_group

        except Exception as e:
            log.critical(f"Unexpected error in create_feature_group: {e}")
            raise

    async def update_feature_group(
        self, group_id: int, update_data: Dict[str, Any]
    ) -> bool:
        """Update a feature group"""
        try:
            statement = (
                update(FeatureGroup)
                .where(FeatureGroup.id == group_id)
                .values(**update_data, updated_at=datetime.now(timezone.utc))
            )
            await self.session.execute(statement)
            await self.session.commit()
            return True

        except Exception as e:
            log.critical(f"Unexpected error in update_feature_group: {e}")
            raise

    async def delete_feature_group(self, group_id: int) -> bool:
        """Delete a feature group"""
        try:
            feature_group = await self.get_feature_group_by_id(group_id)
            if feature_group:
                await self.session.delete(feature_group)
                await self.session.commit()
                return True
            return False

        except Exception as e:
            log.critical(f"Unexpected error in delete_feature_group: {e}")
            raise

    # Features operations
    async def get_features_by_group_id(self, group_id: int) -> List[Features]:
        """Get features by group ID"""
        try:
            statement = select(Features).where(Features.feature_group_id == group_id)
            result = await self.session.execute(statement)
            return result.scalars().all()

        except Exception as e:
            log.critical(f"Unexpected error in get_features_by_group_id: {e}")
            raise

    async def get_feature_by_id(self, feature_id: int) -> Optional[Features]:
        """Get feature by ID"""
        try:
            statement = select(Features).where(Features.id == feature_id)
            result = await self.session.execute(statement)
            return result.scalar_one_or_none()

        except Exception as e:
            log.critical(f"Unexpected error in get_feature_by_id: {e}")
            raise

    async def create_feature(
        self, subscription_feature_data: Dict[str, Any]
    ) -> Features:
        """Create a new subscription feature"""
        try:
            subscription_feature = Features(**subscription_feature_data)
            self.session.add(subscription_feature)
            await self.session.commit()
            await self.session.refresh(subscription_feature)
            return subscription_feature

        except Exception as e:
            log.critical(f"Unexpected error in create_feature: {e}")
            raise

    async def update_feature(
        self, feature_id: int, update_data: Dict[str, Any]
    ) -> bool:
        """Update a subscription feature"""
        try:
            statement = (
                update(Features)
                .where(Features.id == feature_id)
                .values(**update_data, updated_at=datetime.now(timezone.utc))
            )
            await self.session.execute(statement)
            await self.session.commit()
            return True

        except Exception as e:
            log.critical(f"Unexpected error in update_feature: {e}")
            raise

    async def delete_feature(self, feature_id: int) -> bool:
        """Delete a subscription feature"""
        try:
            statement = select(Features).where(Features.id == feature_id)
            result = await self.session.execute(statement)
            subscription_feature = result.scalar_one_or_none()

            if subscription_feature:
                await self.session.delete(subscription_feature)
                await self.session.commit()
                return True
            return False

        except Exception as e:
            log.critical(f"Unexpected error in delete_feature: {e}")
            raise

    async def get_subscription_plan_details(
        db: AsyncSession, plan_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Get subscription plan by ID with feature groups eagerly loaded"""
        try:
            feature_group_alias = aliased(FeatureGroup)
            features_alias = aliased(Features)

            statement = (
                select(SubscriptionPlan)
                .options(
                    joinedload(SubscriptionPlan.feature_group.of_type(feature_group_alias))
                    .joinedload(feature_group_alias.features.of_type(features_alias))
                )
                .order_by(
                    feature_group_alias.id.asc(), 
                    features_alias.id.asc()
                )
            )

            # Apply filter if plan_id is provided
            if plan_id is not None:
                statement = statement.where(SubscriptionPlan.id == plan_id)

            result = await db.execute(statement)
            return result.unique().scalars().first() if plan_id else result.unique().scalars().all()

        except Exception as e:
            log.critical(f"Unexpected error in get_subscription_plan_details: {e}")
            raise

    