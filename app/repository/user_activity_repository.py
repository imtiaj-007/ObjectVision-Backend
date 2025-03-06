from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, update, delete, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.schemas.enums import ActivityTypeEnum
from app.db.models.user_activity_model import ActiveUserPlans, UserActivity
from app.schemas.user_activity_schemas import (
    ActiveUserPlanCreate,
    ActiveUserPlanUpdate,
    UserActivityCreate,
    UserActivityUpdate,
)


class UserActivityRepository:
    """
    Repository for subscription-related database operations including ActiveUserPlans and UserActivity.
    """

    # -------------------- ActiveUserPlans Operations --------------------

    async def create_user_plan(
        db: AsyncSession, plan_data: ActiveUserPlanCreate
    ) -> ActiveUserPlans:
        """
        Create a new active user plan.

        Args:
            plan_data: The data for the new active user plan

        Returns:
            The created ActiveUserPlans instance
        """
        active_plan = ActiveUserPlans(**plan_data.model_dump())
        db.add(active_plan)
        await db.commit()
        await db.refresh(active_plan)
        return active_plan

    async def get_user_plan(db: AsyncSession, plan_id: int) -> Optional[ActiveUserPlans]:
        """
        Get an active user plan by ID.

        Args:
            plan_id: The ID of the active user plan

        Returns:
            The ActiveUserPlans instance if found, None otherwise
        """
        result = await db.execute(
            select(ActiveUserPlans).where(ActiveUserPlans.id == plan_id)
        )
        return result.scalars().first()

    async def get_user_plans_by_user(
        db: AsyncSession, user_id: int
    ) -> List[ActiveUserPlans]:
        """
        Get all active user plans for a specific user.

        Args:
            user_id: The ID of the user

        Returns:
            A list of ActiveUserPlans instances
        """
        result = await db.execute(
            select(ActiveUserPlans)
            .where(ActiveUserPlans.user_id == user_id)
            .order_by(desc(ActiveUserPlans.created_at))
        )
        return result.scalars().all()
    
    async def get_active_user_plans_with_status(
        db: AsyncSession, user_id: int, is_active: bool = True
    ) -> List[ActiveUserPlans]:
        """
        Get all active user plans for a specific user with a specific status.

        Args:
            user_id: The ID of the user
            is_active: The active status to filter by

        Returns:
            A list of ActiveUserPlans instances
        """
        result = await db.execute(
            select(ActiveUserPlans)
            .where(
                and_(
                    ActiveUserPlans.user_id == user_id,
                    ActiveUserPlans.is_active == is_active,
                )
            )
            .order_by(desc(ActiveUserPlans.created_at))
        )
        return result.scalars().all()

    async def get_current_active_plan(db: AsyncSession, user_id: int) -> Optional[ActiveUserPlans]:
        """
        Get the current active plan for a user.

        Args:
            user_id: The ID of the user

        Returns:
            The current ActiveUserPlans instance if found, None otherwise
        """
        result = await db.execute(
            select(ActiveUserPlans)
            .where(
                and_(
                    ActiveUserPlans.user_id == user_id,
                    ActiveUserPlans.is_active == True,
                    or_(
                        ActiveUserPlans.expiry_date == None,
                        ActiveUserPlans.expiry_date > datetime.now(timezone.utc),
                    ),
                )
            )
            .order_by(desc(ActiveUserPlans.expiry_date))
        )
        return result.scalars().first()

    async def update_user_plan(
        self, db: AsyncSession, plan_id: int, plan_data: ActiveUserPlanUpdate
    ) -> Optional[ActiveUserPlans]:
        """
        Update an active user plan.

        Args:
            plan_id: The ID of the active user plan to update
            plan_data: The updated data

        Returns:
            The updated ActiveUserPlans instance if found, None otherwise
        """
        # Filter out None values
        update_data = {k: v for k, v in plan_data.model_dump().items() if v is not None}

        if not update_data:
            # No fields to update
            return await self.get_active_user_plan(plan_id)

        # Add updated_at timestamp
        update_data["updated_at"] = datetime.now(timezone.utc)

        await db.execute(
            update(ActiveUserPlans)
            .where(ActiveUserPlans.id == plan_id)
            .values(**update_data)
        )
        await db.commit()

        return await self.get_active_user_plan(plan_id)

    async def deactivate_user_plans(db: AsyncSession, user_id: int) -> bool:
        """
        Deactivate all plans for a user.

        Args:
            user_id: The ID of the user

        Returns:
            True if the operation was successful
        """
        await db.execute(
            update(ActiveUserPlans)
            .where(
                and_(
                    ActiveUserPlans.user_id == user_id,
                    ActiveUserPlans.is_active == True,
                )
            )
            .values(is_active=False, updated_at=datetime.now(timezone.utc))
        )
        await db.commit()
        return True

    async def delete_user_plan(db: AsyncSession, plan_id: int) -> bool:
        """
        Delete an active user plan.

        Args:
            plan_id: The ID of the active user plan to delete

        Returns:
            True if the operation was successful
        """
        await db.execute(
            delete(ActiveUserPlans).where(ActiveUserPlans.id == plan_id)
        )
        await db.commit()
        return True

    async def check_for_expired_plans(db: AsyncSession) -> List[ActiveUserPlans]:
        """
        Find and deactivate expired plans.

        Returns:
            A list of deactivated ActiveUserPlans instances
        """
        now = datetime.now(timezone.utc)

        # Find expired plans
        result = await db.execute(
            select(ActiveUserPlans).where(
                and_(
                    ActiveUserPlans.is_active == True,
                    ActiveUserPlans.expiry_date <= now,
                )
            )
        )
        expired_plans = result.scalars().all()

        # Deactivate expired plans
        if expired_plans:
            expired_ids = [plan.id for plan in expired_plans]
            await db.execute(
                update(ActiveUserPlans)
                .where(ActiveUserPlans.id.in_(expired_ids))
                .values(is_active=False, updated_at=now)
            )
            await db.commit()

        return expired_plans

    # -------------------- UserActivity Operations --------------------

    async def create_user_activity(
        db: AsyncSession, activity_data: UserActivityCreate
    ) -> UserActivity:
        """
        Create a new user activity record.

        Args:
            activity_data: The data for the new user activity

        Returns:
            The created UserActivity instance
        """
        user_activity = UserActivity(**activity_data.model_dump())
        db.add(user_activity)
        await db.commit()
        await db.refresh(user_activity)
        return user_activity

    async def get_user_activity(db: AsyncSession, activity_id: int) -> Optional[UserActivity]:
        """
        Get a user activity by ID.

        Args:
            activity_id: The ID of the user activity

        Returns:
            The UserActivity instance if found, None otherwise
        """
        result = await db.execute(
            select(UserActivity).where(UserActivity.id == activity_id)
        )
        return result.scalars().first()

    async def get_user_activities_by_plan(
        db: AsyncSession, active_user_plan_id: int
    ) -> List[UserActivity]:
        """
        Get all activities for a specific active user plan.

        Args:
            active_user_plan_id: The ID of the active user plan

        Returns:
            A list of UserActivity instances
        """
        result = await db.execute(
            select(UserActivity)
            .where(UserActivity.active_user_plan_id == active_user_plan_id)
            .order_by(UserActivity.activity_type)
        )
        return result.scalars().all()

    async def get_activity_by_plan_and_type(
        db: AsyncSession, active_user_plan_id: int, activity_type: ActivityTypeEnum
    ) -> Optional[UserActivity]:
        """
        Get a specific activity for a plan by type.

        Args:
            active_user_plan_id: The ID of the active user plan
            activity_type: The type of activity to find

        Returns:
            The UserActivity instance if found, None otherwise
        """
        result = await db.execute(
            select(UserActivity).where(
                and_(
                    UserActivity.active_user_plan_id == active_user_plan_id,
                    UserActivity.activity_type == activity_type,
                )
            )
        )
        return result.scalars().first()

    async def update_user_activity(
        self, db: AsyncSession, activity_id: int, activity_data: UserActivityUpdate
    ) -> Optional[UserActivity]:
        """
        Update a user activity.

        Args:
            activity_id: The ID of the user activity to update
            activity_data: The updated data

        Returns:
            The updated UserActivity instance if found, None otherwise
        """
        # Filter out None values
        update_data = {
            k: v for k, v in activity_data.model_dump().items() if v is not None
        }

        if not update_data:
            # No fields to update
            return await self.get_user_activity(activity_id)

        # Add updated_at timestamp
        update_data["updated_at"] = datetime.now(timezone.utc)

        await db.execute(
            update(UserActivity)
            .where(UserActivity.id == activity_id)
            .values(**update_data)
        )
        await db.commit()

        return await self.get_user_activity(activity_id)

    async def increment_activity_usage(
        self,
        db: AsyncSession,
        active_user_plan_id: int,
        activity_type: ActivityTypeEnum,
        daily_increment: int = 1,
        total_increment: int = 1,
    ) -> Optional[UserActivity]:
        """
        Increment the usage counters for a specific activity.

        Args:
            active_user_plan_id: The ID of the active user plan
            activity_type: The type of activity to update
            daily_increment: The amount to increment daily usage by
            total_increment: The amount to increment total usage by

        Returns:
            The updated UserActivity instance if found, None otherwise
        """
        # First, find the activity
        activity = await self.get_activity_by_plan_and_type(
            active_user_plan_id, activity_type
        )

        if not activity:
            return None

        # Update the usage counts
        await db.execute(
            update(UserActivity)
            .where(and_(UserActivity.id == activity.id))
            .values(
                daily_usage=UserActivity.daily_usage + daily_increment,
                total_usage=UserActivity.total_usage + total_increment,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await db.commit()

        # Return the updated activity
        return await self.get_user_activity(activity.id)

    async def reset_daily_usage(
        db: AsyncSession,
        active_user_plan_id: Optional[int] = None,
        activity_type: Optional[ActivityTypeEnum] = None,
    ) -> int:
        """
        Reset daily usage counters to zero.
        Can be filtered by plan ID and/or activity type.

        Args:
            active_user_plan_id: Optional ID of the active user plan to filter by
            activity_type: Optional activity type to filter by

        Returns:
            The number of records updated
        """
        query = update(UserActivity).values(
            daily_usage=0, updated_at=datetime.now(timezone.utc)
        )

        # Apply filters if provided
        conditions = []
        if active_user_plan_id is not None:
            conditions.append(UserActivity.active_user_plan_id == active_user_plan_id)
        if activity_type is not None:
            conditions.append(UserActivity.activity_type == activity_type)

        if conditions:
            query = query.where(and_(*conditions))

        result = await db.execute(query)
        await db.commit()

        return result.rowcount

    async def delete_user_activity(db: AsyncSession, activity_id: int) -> bool:
        """
        Delete a user activity.

        Args:
            activity_id: The ID of the user activity to delete

        Returns:
            True if the operation was successful
        """
        await db.execute(
            delete(UserActivity).where(UserActivity.id == activity_id)
        )
        await db.commit()
        return True

    async def check_activity_limits(
        self, db: AsyncSession, active_user_plan_id: int, activity_type: ActivityTypeEnum
    ) -> Tuple[bool, bool]:
        """
        Check if the daily and total limits have been reached for an activity.

        Args:
            active_user_plan_id: The ID of the active user plan
            activity_type: The type of activity to check

        Returns:
            A tuple of (daily_limit_reached, total_limit_reached)
        """
        activity = await self.get_activity_by_plan_and_type(
            active_user_plan_id, activity_type
        )

        if not activity:
            return False, False

        daily_limit_reached = False
        total_limit_reached = False

        if (
            activity.daily_limit is not None
            and activity.daily_usage >= activity.daily_limit
        ):
            daily_limit_reached = True

        if (
            activity.total_limit is not None
            and activity.total_usage >= activity.total_limit
        ):
            total_limit_reached = True

        return daily_limit_reached, total_limit_reached

    # -------------------- Combined Operations --------------------

    async def initialize_plan_activities(
        self, db: AsyncSession, active_user_plan: ActiveUserPlans, activity_configs: List[Dict[str, Any]]
    ) -> List[UserActivity]:
        """
        Initialize all activities for a newly created plan.

        Args:
            active_user_plan: The ActiveUserPlans instance
            activity_configs: A list of dictionaries containing activity configurations

        Returns:
            A list of created UserActivity instances
        """
        activities = []

        for config in activity_configs:
            activity_data = UserActivityCreate(
                active_user_plan_id=active_user_plan.id, **config
            )
            activity = await self.create_user_activity(activity_data)
            activities.append(activity)

        return activities

    async def get_user_subscription_summary(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """
        Get a summary of a user's subscription status.

        Args:
            user_id: The ID of the user

        Returns:
            A dictionary with subscription summary data
        """
        # Get current active plan
        current_plan = await self.get_current_active_plan(user_id)

        # Get all activities if there is an active plan
        activities = []
        if current_plan:
            activities = await self.get_user_activities_by_plan(current_plan.id)

        # Build summary
        summary = {
            "has_active_plan": current_plan is not None,
            "current_plan": current_plan.model_dump() if current_plan else None,
            "activities": [activity.model_dump() for activity in activities],
            "limits_reached": {},
        }

        # Check if any limits are reached
        if current_plan:
            for activity in activities:
                daily_reached, total_reached = await self.check_activity_limits(
                    current_plan.id, activity.activity_type
                )
                summary["limits_reached"][activity.activity_type.value] = {
                    "daily_limit_reached": daily_reached,
                    "total_limit_reached": total_reached,
                }

        return summary
