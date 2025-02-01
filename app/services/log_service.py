from typing import Dict, List, Any
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.configuration.config import settings
from app.tasks.taskfiles.log_task import store_log_entry
from app.repository.log_repository import LogRepository
from app.schemas.log_schema import LogCreate
from app.utils.logger import log



class LogService:
    @staticmethod
    def create_log(log_data: Dict[str, Any]) -> None:
        """Create a single log entry"""
        try:
            # Validate data
            validated_data = LogCreate(**log_data)

            # Send to Celery task
            taskId = store_log_entry.delay(validated_data.model_dump_json())
            return taskId

        except Exception as e:
            log.error("Failed to create log entry", exc_info=e)
            raise
    
    @staticmethod
    async def get_task_status(task_id):
        """
        Retrieve the status of a Celery task by its task ID.
        
        Args:
            task_id (str): The unique identifier of the Celery task
        
        Returns:
            dict: Task status information
        """
        # loop = asyncio.get_event_loop()
        # task = await loop.run_in_executor(
        #     None, 
        #     lambda: AsyncResult(task_id, app=celery_app)
        # )
        
        # print({
        #     'task_id': task_id,
        #     'status': task.status,
        #     'result': task.result if task.ready() else None,
        #     'successful': task.successful()
        # })
        pass
    
    @staticmethod
    async def create_logs_batch(log_data_batch: List[Dict[str, Any]]) -> None:
        """Create multiple log entries in batch"""
        for i in range(0, len(log_data_batch), settings.BATCH_SIZE):
            batch = log_data_batch[i:i + settings.BATCH_SIZE]
            # validated_batch = [LogData(**data).dict() for data in batch]
            store_log_entry.delay(batch)

    @staticmethod
    async def log_exception(
        request: Request, db: AsyncSession, message: str, exc: Exception, level="ERROR"
    ):
        """Stores exception details in the database."""
        await LogRepository.store_log(
            session=db,
            message=message,
            log_level=level,
            request_id=request.headers.get("X-Request-ID"),
            request_url=str(request.url),
            request_method=request.method,
            ip_address=request.client.host if request.client else None,
            error_code=str(getattr(exc, "code", "500")),
            stack_trace=str(exc)
        )
