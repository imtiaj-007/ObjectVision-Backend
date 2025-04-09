import json
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.tasks.celery import celery_app
from app.tasks.taskfiles.base import AsyncDatabaseTask
from cache.activity_tracker import user_activity_tracker

from app.services.subscription_service import SubscriptionService
from app.repository.payment_order_repository import PaymentOrderRepository
from app.repository.user_activity_repository import UserActivityRepository

from app.schemas.payment_schemas import OrderCreate, OrderUpdate
from app.schemas.subscription_schema import SubscriptionDetails
from app.schemas.user_activity_schemas import ActiveUserPlanCreate, ActiveUserPlanUpdate, UserActivityCreate, UserActivityUpdate
from app.schemas.enums import PaymentStatus
from app.utils.helpers import get_plan_keys, create_activity_entries
from app.utils.logger import log


@celery_app.task(
    bind=True,
    base=AsyncDatabaseTask,
    name="tasks.subscription.store_order_data",
    queue="subscription",
)
def store_order_task(
    self,
    user_id: int,
    order_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Celery task to store different types of data in the database.
    Uses async wrapper around async code to make it compatible with Celery.
    """

    async def async_wrapper():
        async with self.get_async_session() as session:
            data = OrderCreate(user_id=user_id, **order_data)
            await PaymentOrderRepository.store_order(session, data.model_dump())

        await self.cleanup()

    try:
        AsyncDatabaseTask.run_async(async_wrapper())
        log.success(f"{order_data.get('receipt')} stored in database successfully")

    except Exception as exc:
        log.error(
            f"Failed to store {order_data.get('receipt')} in database. Error: {exc}"
        )


@celery_app.task(
    bind=True,
    base=AsyncDatabaseTask,
    name="tasks.subscription.update_order_data",
    queue="subscription",
)
def update_order_task(
    self,
    razorpay_order_id: str,
    payment_status: str,
    user: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Celery task to store different types of data in the database.
    Uses async wrapper around async code to make it compatible with Celery.
    """

    async def async_wrapper():
        try:
            async with self.get_async_session() as session:
                order_data = await PaymentOrderRepository.get_order_details(
                    db=session, razorpay_order_id=razorpay_order_id
                )
                if not order_data:
                    log.critical(f"Order data not found with id: {razorpay_order_id}")
                    return

                data = OrderUpdate(
                    **{
                        **order_data.model_dump(),
                        "status": PaymentStatus(payment_status),
                        "updated_at": datetime.now(timezone.utc),
                    },
                )

                await PaymentOrderRepository.update_order(
                    db=session, order_id=order_data.id, update_data=data.model_dump()
                )

                plan_details = (
                    await SubscriptionService.get_subscription_plan_with_features(
                        db=session, plan_id=data.plan_id
                    )
                )

                await create_plan_and_activity(
                    db=session, user_id=user.get("id"), plan_data=plan_details
                )

            await self.cleanup()

        except Exception as e:
            log.error(f"Error in Async wrapper of update_order_task: {str(e)}")

    try:
        AsyncDatabaseTask.run_async(async_wrapper())
        log.success(f"Order: {razorpay_order_id} is successfully updated.")

    except Exception as exc:
        log.error(f"Failed to update Order: {razorpay_order_id}.\nError: {str(exc)}")


@celery_app.task(
    bind=True,
    base=AsyncDatabaseTask,
    name="tasks.subscription.map_purchased_plan_with_user",
    queue="subscription",
)
def map_purchased_plan_with_user_task(
    self,
    user_id: int,
    plan_data: Dict[str, Any],
    update_plan: bool = False,
    purchased_date: datetime = datetime.now(),
) -> Dict[str, Any]:
    """
    Celery task to store different types of data in the database.
    Uses async wrapper around async code to make it compatible with Celery.
    """

    async def async_wrapper():
        try:
            async with self.get_async_session() as session:
                await create_plan_and_activity(
                    db=session,
                    user_id=user_id,
                    plan_data=plan_data,
                    purchased_date=purchased_date,
                    update_plan=update_plan
                )

            await self.cleanup()

        except Exception as e:
            log.error(
                f"Error in Async wrapper of map_purchased_plan_with_user_task: {str(e)}"
            )

    try:
        AsyncDatabaseTask.run_async(async_wrapper())
        log.success(
            f"{plan_data.get('name')} plan is successfully mapped with user_id: {user_id}"
        )

    except Exception as exc:
        log.error(
            f"Failed to map {plan_data.get('name')} plan with user_id: {user_id}.\nError: {str(exc)}"
        )


@celery_app.task(
    bind=True,
    base=AsyncDatabaseTask,
    name="tasks.subscription.update_user_activity",
    queue="subscription",
)
def update_user_activity_task(
    self,
    username: str,
    user_activities: Dict[str, Dict[str, Any]],
    file_size: int,
    service_count: int,
):
    """
    Celery task to update user activities like Image, Video and Storage Usage.
    Uses async wrapper around async code to make it compatible with Celery.
    Also updates the Redis cache to keep it in sync with database.
    """

    if isinstance(user_activities, str):
        try:
            user_activities = json.loads(user_activities)
        except json.JSONDecodeError as e:
            log.error(f"Failed to decode user_activities: {str(e)}")
            return

    async def async_wrapper():
        try:
            async with self.get_async_session() as session:
                image_activity = user_activities.get("image_activity", None)
                video_activity = user_activities.get("video_activity", None)
                storage_activity = user_activities.get("storage_activity", None)

                updated_activities = []

                if image_activity:
                    image_activity["daily_usage"] += 1
                    image_activity["total_usage"] += 1

                    updated_image_activity = await UserActivityRepository.update_user_activity(
                        db=session,
                        activity_id=image_activity.get("id"),
                        activity_data=UserActivityUpdate(**image_activity),
                    )
                    updated_activities.append(updated_image_activity)

                if video_activity:
                    video_activity["daily_usage"] += 1
                    video_activity["total_usage"] += 1

                    updated_video_activity = await UserActivityRepository.update_user_activity(
                        db=session,
                        activity_id=video_activity.get("id"),
                        activity_data=UserActivityUpdate(**video_activity),
                    )
                    updated_activities.append(updated_video_activity)

                if storage_activity:
                    storage_usage = (file_size * (service_count + 1))
                    storage_activity["daily_usage"] += storage_usage
                    storage_activity["total_usage"] += storage_usage

                    updated_storage_activity = await UserActivityRepository.update_user_activity(
                        db=session,
                        activity_id=storage_activity.get("id"),
                        activity_data=UserActivityUpdate(**storage_activity),
                    )
                    updated_activities.append(updated_storage_activity)

                if username and updated_activities:
                    for activity in updated_activities:
                        user_activity_tracker.store_activity(username, activity)

            await self.cleanup()

        except Exception as e:
            log.error(
                f"Error in Async wrapper of update_user_activity_task: {str(e)}"
            )

    try:
        AsyncDatabaseTask.run_async(async_wrapper())
        log.success(f"User activities updated successfully.")

    except Exception as exc:
        log.error(f"Unexpected error in update_user_activity_task: {str(exc)}")


async def create_plan_and_activity(
    db: AsyncSession,
    user_id: int,
    plan_data: Dict[str, Any],
    purchased_date: datetime = datetime.now(),
    update_plan: bool = False
):
    try:
        active_plan = await UserActivityRepository.get_current_active_plan(
            db, user_id=user_id
        )
        print("active_plan: ", active_plan)

        # Prepare data as per requirements
        plan_details = SubscriptionDetails(**plan_data)
        limits_map = get_plan_keys(plan_details)

        plan_validity = limits_map.get("validity", 15)
        backup_duration = limits_map.get("image_backup_duration") or limits_map.get(
            "video_backup_duration", 30
        )

        expiry_date = (
            purchased_date + timedelta(days=plan_validity) if (update_plan or not active_plan) else None
        )
        backup_till = (
            purchased_date + timedelta(days=backup_duration)
            if (update_plan or not active_plan)
            else None
        )

        # Prepare extra data
        extra_data = {
            "is_active": not active_plan,
            "expiry_date": expiry_date,
            "backup_till": backup_till,
        }

        # First Store / Update User Plan mapping
        if not update_plan:
            data = ActiveUserPlanCreate(
                user_id=user_id,
                plan_id=plan_details.id,
                plan_name=plan_details.name,
                description=plan_details.description,
                **extra_data,
            )
            user_plan = await UserActivityRepository.create_user_plan(db, data)

            # Create user activity rows
            activity_rows = create_activity_entries(user_plan.id, limits_map)
            for activity in activity_rows:
                row_data = UserActivityCreate(**activity)
                await UserActivityRepository.create_user_activity(
                    db, activity_data=row_data
                )        
        else:
            data = ActiveUserPlanUpdate(
                expiry_date=expiry_date,
                backup_till=backup_till
            )
            await UserActivityRepository.update_user_plan(db, active_plan.id, data)        

    except Exception as e:
        log.error(f"Error in create_plan_and_activity method: {str(e)}")
