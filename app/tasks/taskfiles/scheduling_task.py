from datetime import datetime
from app.configuration.config import settings
from app.tasks.celery import celery_app
from app.tasks.taskfiles.base import AsyncDatabaseTask
from app.tasks.taskfiles.subscription_task import map_purchased_plan_with_user_task

from app.services.subscription_service import SubscriptionService
from app.repository.session_repository import SessionRepository
from app.repository.user_activity_repository import UserActivityRepository
from app.utils import helpers
from app.utils.logger import log


@celery_app.task(
    bind=True,
    base=AsyncDatabaseTask,
    max_retries=settings.MAX_RETRIES,
    name="tasks.scheduling.expire_sessions",
    queue="scheduling"
)
def expire_sessions_task( self ):
    """ Expire sessions that are expired. """
    async def async_wrapper():
        async with self.get_async_session() as session:
            log.info("♻️ Starting expired sessions update job")
            try:
                updated_count = await SessionRepository.update_expired_sessions(session)
                
                msg = ""
                if(updated_count == 0):
                    msg = "🔰 All sessions are active, no need to update."
                else:
                    msg = f"✅ Successfully updated {updated_count} expired session{'s' if updated_count > 1 else ''}"
                
                log.success(msg)
                    
            except Exception as e:
                log.error(f"Error in async wrapper of expire_sessions_task: {str(e)}")

        await self.cleanup()

    try:                
        AsyncDatabaseTask.run_async(async_wrapper())
        
    except Exception as e:
        log.error(f"Failed to expire sessions: {str(e)}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task(
    bind=True,
    base=AsyncDatabaseTask,
    max_retries=settings.MAX_RETRIES,
    name="tasks.scheduling.delete_cached_files",
    queue="scheduling"
)
def delete_cached_files_task( self ):
    """ Delete cached files in local_storage after each hour """
    try:                
        pass
        
    except Exception as e:
        log.error(f"Failed to delete cached files: {str(e)}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task(
    bind=True,
    base=AsyncDatabaseTask,
    max_retries=settings.MAX_RETRIES,
    name="tasks.scheduling.process_subscriptions",
    queue="scheduling"
)
def process_subscriptions_task( self ):
    """ Expire and auto-activate user subscriptions """
    async def async_wrapper():
        async with self.get_async_session() as session:
            expired_plans = await UserActivityRepository.expire_user_plans(db=session)
            if expired_plans:
                for plan in expired_plans:
                    queued_plan = await UserActivityRepository.auto_activate_user_plan(
                        session, plan.user_id
                    )
                    if queued_plan:
                        plan_details = await SubscriptionService.get_subscription_plan_with_features(
                            db=session, plan_id=queued_plan.plan_id
                        )

                        plan_details_dict = helpers.serialize_datetime_object(plan_details)
                        map_purchased_plan_with_user_task.apply_async(
                            args=(plan.user_id, plan_details_dict, True),
                            countdown=60,
                        )

        await self.cleanup()

    try:                
        AsyncDatabaseTask.run_async(async_wrapper())

    except Exception as e:
        log.error(f"Failed to process subscriptions: {str(e)}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task(
    bind=True,
    base=AsyncDatabaseTask,
    max_retries=settings.MAX_RETRIES,
    name="tasks.scheduling.reset_daily_usage",
    queue="scheduling"
)
def reset_daily_usage_task( self ):
    """ Reset daily usages of user activities """
    async def async_wrapper():
        async with self.get_async_session() as session:
            await UserActivityRepository.reset_daily_usage(
                db=session
            )

        await self.cleanup()

    try:                
        AsyncDatabaseTask.run_async(async_wrapper())
        
    except Exception as e:
        log.error(f"Failed to reset daily usage: {str(e)}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
