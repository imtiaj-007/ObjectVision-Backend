import json
from app.configuration.config import settings
from app.db.database import db_session_manager
from app.db.models.log_model import Log

from app.tasks.celery import celery_app
from app.tasks.taskfiles.base import BaseTask
from app.utils.logger import log

@celery_app.task(
    bind=True,
    base=BaseTask,
    max_retries=settings.MAX_RETRIES,
    name="tasks.logging.store_logs",
    queue="logging"
)
def store_log_entry( self, log_data: dict ):
    """Store a single log entry"""
    print("log_data: ", log_data)
    try:                
        if isinstance(log_data, str):
            log_data = json.loads(log_data)

        # Store in database
        log_entry = Log(**log_data)            
        with db_session_manager.get_db_synchronous() as db:
            
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
            print("log_entry: ", log_entry)
            
        return log_entry.id
        
    except Exception as e:
        log.error(f"Failed to store log entry: {e}")
        # log.error(traceback.format_exc())
        # current_task.update_state(state='FAILURE', meta={'exc': str(e)})
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))