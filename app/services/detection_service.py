import os
import aiofiles
from PIL import Image
from io import BytesIO
from datetime import datetime
from typing import Optional, Dict, List
from fastapi import UploadFile, HTTPException

from app.configuration.config import settings
from app.tasks.taskfiles.detection_task import store_image_data_task
from app.helpers.file_types import FileConfig, FileType
from app.utils.logger import log

from app.services.yolo_service import YOLOProcessor, config
from app.schemas.image_schema import (
    ImageMetadata,
    CreateImage,
    UpdateImage,
)


class DetectionService:
    services: List[str] = ["detection", "segmentation", "classification", "pose"]

    @classmethod
    async def save_file_locally(cls, file: UploadFile, file_path: str) -> bool:
        """Save uploaded file to local storage."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            async with aiofiles.open(file_path, "wb") as buffer:
                await file.seek(0)
                content = await file.read()
                await buffer.write(content)
            return True
        except Exception as e:
            log.error(f"Error saving file locally: {e}")
            return False

    @classmethod
    async def get_image_properties(cls, file: UploadFile):
        """Get image properties while properly handling file pointer position."""
        try:
            await file.seek(0)
            contents = await file.read()

            image_buffer = BytesIO(contents)
            image = Image.open(image_buffer)

            properties = {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
            }

            await file.seek(0)
            return properties

        except Exception as e:
            log.error(f"Error getting image properties: {e}")
            raise HTTPException(status_code=400, detail="Invalid image file or format")

    @classmethod
    async def image_detection(
        cls,
        file: UploadFile,
        model_size: str = "small",
        requested_services: Optional[List[str]] = None,
    ) -> Dict:
        """
        Process image through multiple detection services and store results.

        Args:
            file: Uploaded image file
            requested_services: Set of specific services to run (runs all if None)
            db: Database session

        Returns:
            Dict containing processing results and S3 URL
        """
        try:
            # Validate file
            file_details = FileConfig.validate_file(
                filename=file.filename, file_type=FileType.IMAGE, file_size=file.size
            )

            # Generate unique filename and path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{file_details['filename']}"
            file_path = os.path.join(
                settings.BASE_DIR,
                "uploads\images",
                unique_filename,
            )

            img_properties = await cls.get_image_properties(file)

            # Construct metadata
            img_metadata = ImageMetadata(
                extension=file_details["extension"],
                mime_type=file_details["mime_type"],
                file_type=file_details["file_type"],
                file_size=file_details["file_size"],
                width=img_properties["width"],
                height=img_properties["height"],
            )

            # Save file locally
            if not await cls.save_file_locally(file, file_path):
                raise HTTPException(
                    status_code=500, detail="Failed to save file locally"
                )

            # Process image through requested or all services
            services_to_run = requested_services or cls.services
            processor = YOLOProcessor(
                config, model_size=model_size, model_types=services_to_run
            )
            results = {}

            for service in services_to_run:
                if service not in cls.services:
                    continue
                results[service] = processor.process_image(
                    file_name=unique_filename, image_path=file_path, model_type=service
                )

            # Store image_details, detection_results and processed_images in DB and AWS_S3
            img_data = CreateImage(
                filename=unique_filename,
                image_metadata=img_metadata,
                local_file_path=file_path,
            )

            store_image_data_task.delay(
                image_data=img_data.model_dump(),
                services=services_to_run,
                detection_data=results,
            )

            return {"filename": unique_filename, "results": results}

        except Exception as e:
            log.error(f"Unexpected error occurred in image detection: {e}")
            raise HTTPException(
                status_code=500, detail=f"Image detection failed: {str(e)}"
            )

