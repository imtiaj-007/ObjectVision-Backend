from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repository.user_activity_repository import UserActivityRepository
from app.utils.logger import log


class UserActivityService:
    """
    Service class for handling business logic related to User subscriptions and Activity.
    """

    # UserActivity service methods
    async def get_user_subscription_plans(
        db: AsyncSession, user_id: int
    ) -> List[Dict[str, Any]]:
        """Create a new subscription plan with validation."""
        plans = []
        try:
            plans = await UserActivityRepository.get_user_plans_by_user(
                db, user_id
            )
            return plans

        except Exception as e:
            log.error(
                f"UserActivityService Error: -> [get_user_subscription_plans], error: {str(e)}"
            )
            raise

    async def get_active_user_subscription_plans(
        db: AsyncSession, user_id: int, is_active: bool = True
    ) -> List[Dict[str, Any]]:
        """Create a new subscription plan with validation."""
        plans = []
        try:
            plans = await UserActivityRepository.get_active_user_plans_with_status(
                db, user_id, is_active
            )
            return plans

        except Exception as e:
            log.error(
                f"UserActivityService Error: -> [get_active_user_subscription_plans], error: {str(e)}"
            )
            raise

    # UserActivity service methods
    async def get_user_activities(
        db: AsyncSession, user_id: int
    ) -> List[Dict[str, Any]]:
        """Create a new subscription plan with validation."""
        try:
            active_plan = await UserActivityRepository.get_current_active_plan(
                db, user_id
            )
            if not active_plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No active plan found for the user.",
                )

            user_activities = await UserActivityRepository.get_user_activities_by_plan(
                db, active_plan.id
            )
            return user_activities

        except Exception as e:
            log.error(
                f"UserActivityService Error: -> [get_user_activities], error: {str(e)}"
            )
            raise
