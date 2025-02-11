from app.configuration.config import settings
from app.tasks.celery import celery_app
from app.tasks.taskfiles.base import BaseTask
from app.utils.blacklist import add_token_to_blacklist
from app.utils.logger import log


@celery_app.task(
    bind=True,
    base=BaseTask,
    max_retries=settings.MAX_RETRIES,
    name="tasks.token.blacklist_token",
    queue="token"
)
def blacklist_token_task(self, token: str):
    """Celery task to blacklist a token with expiration."""
    try:                
        add_token_to_blacklist(token, 900) # 15 min Expiry
        return {"status": "Token blacklisted successfully"}
        
    except Exception as e:
        log.error(f"Failed to blacklist token: {e}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))