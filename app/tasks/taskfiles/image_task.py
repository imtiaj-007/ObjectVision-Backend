from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timezone

from app.configuration.config import settings
from app.tasks.celery import celery_app
from app.tasks.taskfiles.base import BaseTask, AsyncDatabaseTask
from app.services.file_service import upload_processed_image

from app.repository.detection_repository import DetectionRepository
from app.schemas.enums import FileType
from app.schemas.image_schema import UpdateImage, UpdateProcessedImage
from app.utils.logger import log
from app.utils.file_compressor import process_and_convert_to_webp


@celery_app.task(
    bind=True,
    base=BaseTask,
    max_retries=settings.MAX_RETRIES,
    name="tasks.image.compress_processed_image",
    queue="image",
)
def compress_processed_image_task(
    self,
    image_path: str,
    output_dir: str = None,
    quality: int = 50,
    resize_factor: float = None,
    filename: str = None,
):
    try:        
        output_path = process_and_convert_to_webp(
            original_image_path=str(Path(image_path).with_suffix('.jpg')),
            output_dir=output_dir,
            quality=quality,
            resize_factor=[resize_factor] if resize_factor else None
        )
        
        # If a custom filename is provided, rename the file
        if filename and output_path:
            original_path = Path(output_path)
            new_path = original_path.parent / f"{filename}.webp"
            
            original_path.rename(new_path)
            output_path = str(new_path)
            log.info(f"Renamed output file to: {new_path}")
            
        log.info(f"Successfully compressed image to: {output_path}")
        return output_path
    
    except Exception as exc:
        log.error(f"Failed to compress image: {str(exc)}")        


@celery_app.task(
    bind=True,
    base=AsyncDatabaseTask,
    name="tasks.image.upload_image_to_S3",
    queue="image",
)
def upload_image_to_S3_task(
    self,
    image_id: int,
    image_type: str,
    file_path: str,
    cloud_dir: str
) -> Dict[str, Any]:
    """
    Celery task to store processed images in AWS S3.
    """

    async def async_wrapper(file_key: str):
        async with self.get_async_session() as session:
            await update_image_data_in_DB(
                session, image_id, image_type, file_key
            )
        await self.cleanup()

    try:
        file_key = upload_processed_image(
            local_file_path=file_path,
            destination_folder=cloud_dir,
            file_type=FileType.IMAGE
        )

        AsyncDatabaseTask.run_async(async_wrapper(file_key))
        log.success(f"File successfully uploaded to S3: {file_key}")

    except Exception as exc:
        log.error(f"Failed to upload image to S3: {str(exc)}")


async def update_image_data_in_DB(
    session: AsyncSession,
    image_id: int,
    image_type: str,
    cloud_path: str
):
    try:
        if image_type == 'original_image':
            img_data = UpdateImage(
                cloud_file_path=cloud_path,
                processed=True,
                updated_at=datetime.now(timezone.utc)
            )
            await DetectionRepository.update_image_details(
                db=session,
                image_id=image_id,
                **img_data.model_dump(),
            )
        else:
            pimg_data = UpdateProcessedImage(
                cloud_processed_path=cloud_path,
                updated_at=datetime.now(timezone.utc)
            )
            await DetectionRepository.update_processed_image_details(
                db=session,
                processed_id=image_id,
                **pimg_data.model_dump(),
            )

    except Exception as e:
        log.error(f"Unexpected error occurred in update_image_data_in_DB: {str(e)}")
        raise