from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from app.tasks.celery import celery_app
from app.tasks.taskfiles.base import AsyncDatabaseTask
from app.utils.logger import log

from app.repository.detection_repository import DetectionRepository
from app.schemas.image_schema import ProcessedImageData
from app.schemas.detection_schema import DetectionData, ModelTypeEnum
from app.tasks.taskfiles.image_task import upload_image_to_S3_task


@celery_app.task(
    bind=True,
    base=AsyncDatabaseTask,
    name="tasks.detection.store_image_data",
    queue="detection",
)
def store_image_data_task(
    self,
    user_id: int,
    username: str,
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
            await store_image_data_in_DB(
                session, user_id, username, image_data, services, detection_data
            )
        await self.cleanup()

    try:
        AsyncDatabaseTask.run_async(async_wrapper())
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
    user_id: int,
    username: str,
    image_data: Dict[str, Any],
    services: List[str],
    detection_data: Dict[str, Any],
):
    """Async function to store data in the database."""
    try:
        image_data["user_id"] = user_id
        image = await DetectionRepository.store_image_details(
            db=session, image_data=image_data
        )

        upload_image_to_S3_task.apply_async(
            args=(
                image.id,
                "original_image",
                image.local_file_path,
                f"{username}/uploads",
            ),
            countdown=60,
        )

        for service in services:
            temp_data = detection_data.get(service.upper())
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

            upload_image_to_S3_task.apply_async(
                args=(
                    p_image.id,
                    "processed_image",
                    local_path,
                    f"{username}/predictions/{service}",
                ),
                countdown=60,
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
