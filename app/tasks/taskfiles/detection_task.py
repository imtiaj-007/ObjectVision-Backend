import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from app.tasks.celery import celery_app
from app.tasks.taskfiles.base import AsyncDatabaseTask
from app.utils.logger import log

from app.repository.detection_repository import DetectionRepository
from app.schemas.image_schema import ProcessedImageData
from app.schemas.detection_schema import DetectionData, ModelTypeEnum

# Database model imports for Runtime issue
from app.db.models.user_model import User
from app.db.models.session_model import UserSession
from app.db.models.otp_model import OTP
from app.db.models.image_model import Image
from app.db.models.detection_model import Detection
from app.db.models.processed_image_model import ProcessedImage
from app.db.models.log_model import Log


def run_async(coro):
    """Safely run an async coroutine in a sync context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        return loop.run_until_complete(coro)
    finally:
        if loop.is_running():
            loop.close()


@celery_app.task(
    bind=True,
    base=AsyncDatabaseTask,
    name="tasks.detection.store_image_data",
    queue="detection",
)
def store_image_data_task(
    self,
    image_data: Dict[str, Any],
    services: List[str],
    detection_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Celery task to store different types of data in the database.
    Uses async wrapper around async code to make it compatible with Celery.
    """

    async def async_wrapper():
        async with self.get_async_session() as session:
            await store_image_data_in_DB(session, image_data, services, detection_data)
        await self.cleanup()

    try:
        run_async(async_wrapper())
        return {
            "status": 1,
            "message": f"{image_data.get('filename')}, related images and detection data stored in database successfully",
        }

    except Exception as exc:
        log.error(
            f"Failed to store {image_data.get('filename')} in database.\nImage data: {image_data}.\nDetection data: {detection_data}.\n Error: {exc}",
            exc_info=True,
        )
        return {"status": 0, "message": f"An error occurred: {exc}"}


async def store_image_data_in_DB(
    session: AsyncSession,
    image_data: Dict[str, Any],
    services: List[str],
    detection_data: Dict[str, Any],
):
    """Async function to store data in the database."""
    try:
        image = await DetectionRepository.store_image_details(
            db=session, image_data=image_data
        )

        for service in services:
            temp_data = detection_data.get(service)
            local_path = temp_data.get("output_path")
            m_type = temp_data.get("model_type").upper()
            del temp_data["model_type"]

            p_data = ProcessedImageData(
                original_image_id=image.id,
                local_processed_path=local_path,
                processed_type=ModelTypeEnum(m_type).value,
            )

            p_image = await DetectionRepository.store_processed_image_details(
                db=session, processed_data=p_data.model_dump()
            )

            d_data = DetectionData(
                processed_image_id=p_image.id,
                parent_image_id=image.id,
                model_type=ModelTypeEnum(m_type).value,
                **temp_data,
            )

            await DetectionRepository.store_detection_details(
                db=session, detection_data=d_data.model_dump()
            )

    except Exception as e:
        log.error(f"Unexpected error occurred in store_image_data_in_DB: {e}")
        raise