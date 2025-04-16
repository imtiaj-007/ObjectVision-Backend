import os
import asyncio
import aiofiles
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageFile
from datetime import datetime
from typing import Dict, List, Any, Union, Optional
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.configuration.yolo_processor import YOLOProcessorSingleton
from app.schemas.enums import WebSocketMessageType, ModelTypeEnum
from app.schemas.user_schema import UserData
from app.schemas.detection_schema import DetectionRequest
from app.schemas.image_schema import ImageMetadata, CreateImage 
from app.repository.detection_repository import DetectionRepository

from app.configuration.ws_manager import WSConnectionManager
from app.tasks.taskfiles.detection_task import store_image_data_task
from app.helpers.file_types import FileConfig, FileType
from cache.file_tracker import local_file_tracker
from app.utils.logger import log


ImageFile.LOAD_TRUNCATED_IMAGES = True 

class DetectionService:
    services: List[str] = ["detection", "segmentation", "classification", "pose"]

    @classmethod
    async def save_file_locally(cls, file: UploadFile, file_path: Union[Path, str]) -> bool:
        """Save uploaded file to local storage after converting to WebP and compressing."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Read the file content
            await file.seek(0)
            content = await file.read()

            with Image.open(BytesIO(content)) as image:
                if image.mode in ("RGBA", "P"):
                    image = image.convert("RGB")

                # Determine compression quality
                quality = 75 if file.size < 1024 * 1024 else 50

                # Convert to WebP with compression
                webp_buffer = BytesIO()
                image.save(webp_buffer, format="WEBP", quality=quality)
                webp_buffer.seek(0)

            # Save the compressed WebP image to the specified file path
            async with aiofiles.open(file_path, "wb") as buffer:
                await buffer.write(webp_buffer.getvalue())

            return True

        except Exception as e:
            log.error(f"Error saving file locally: {str(e)}")
            return False

    @classmethod
    async def get_image_properties(cls, file_path: str):
        """Get image properties from the stored file on the server."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Image file not found"
                )

            async with aiofiles.open(file_path, "rb") as buffer:
                content = await buffer.read()
                image = Image.open(BytesIO(content))

            properties = {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
            }

            return properties

        except Exception as e:
            log.error(f"Error getting image properties: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Invalid image file or format"
            )

    @staticmethod
    async def get_detection_results(
        db: AsyncSession, page: int, limit: int, user_id: int, image_id: Optional[int]
    ) -> Dict[str, Any]:
        try:
            offset = (page - 1) * limit
            result = await DetectionRepository.get_detection_details(
                db=db, limit=limit, offset=offset, user_id=user_id, image_id=image_id
            )                        
            return result

        except Exception as e:
            log.error(f"Unexpected error in get_detection_results service: {str(e)}")
            raise

    @classmethod
    async def image_detection_ws(
        cls,
        file: UploadFile,
        request_data: DetectionRequest,
        user_data: UserData,
        client_id: str,
        connection_manager: WSConnectionManager,
        task_id: str
    ) -> Dict[str, Any]:
        """
        Process image through multiple detection services and stream results via WebSocket.
        Uses a singleton pattern for YOLO processor to prevent memory leaks.

        Args:
            file: Uploaded image file
            request_data: Detection request parameters
            user_data: User data
            client_id: Client identifier for WebSocket communication
            connection_manager: WebSocket connection manager instance
            task_id: Unique task identifier
            
        Returns:
            Dict containing final processing results
        """
        try:
            # Validate file
            file_details = FileConfig.validate_file(
                filename=file.filename, 
                file_type=FileType.IMAGE, 
                file_size=file.size
            )

            # Generate unique filename and path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_without_extension = os.path.splitext(file_details['filename'])[0]
            unique_filename = f"{timestamp}_{filename_without_extension}.webp"

            file_path = Path(f"uploads/images/{unique_filename}")

            # Send progress update
            await connection_manager.send_message(
                client_id=client_id,
                message={
                    "type": WebSocketMessageType.PROGRESS,
                    "task_id": task_id,
                    "progress": 10,
                    "message": "Saving and preparing uploaded file"
                }
            )

            # Save file locally
            if not await cls.save_file_locally(file, file_path):
                await connection_manager.send_message(
                    client_id=client_id,
                    message={
                        "type": WebSocketMessageType.ERROR,
                        "task_id": task_id,
                        "message": "Failed to save file locally"
                    }
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                    detail="Failed to save file locally"
                )

            # Send progress update
            await connection_manager.send_message(
                client_id=client_id,
                message={
                    "type": WebSocketMessageType.PROGRESS,
                    "task_id": task_id,
                    "progress": 20,
                    "message": "File saved, initializing detection models"
                }
            )

            # Process image through requested or all services
            services_to_run: List[str] = request_data.requested_services or cls.services

            # Get singleton instance of YOLO processor
            processor = YOLOProcessorSingleton.get_instance(
                model_size=request_data.model_size, 
                model_types=services_to_run
            )
            YOLOProcessorSingleton.register_task(task_id, f"{request_data.model_size}_{','.join(sorted(services_to_run))}")

            results = {}
            output_paths: List[str] = []

            # Calculate progress increments based on number of services
            progress_per_service = 60 / len(services_to_run) 
            current_progress = 20

            await connection_manager.send_message(
                client_id=client_id,
                message={
                    "type": WebSocketMessageType.PROGRESS,
                    "task_id": task_id,
                    "progress": current_progress,
                    "message": f"Models initialized, processing with {', '.join(services_to_run)} services"
                }
            )

            # Refresh connection TTL before potentially long-running operations
            await connection_manager.refresh_connection(client_id)

            try:
                for i, service in enumerate(services_to_run):
                    if service not in cls.services:
                        continue

                    # Send progress update - starting this service
                    current_progress += progress_per_service / 2
                    await connection_manager.send_message(
                        client_id=client_id,
                        message={
                            "type": WebSocketMessageType.PROGRESS,
                            "task_id": task_id,
                            "progress": current_progress,
                            "message": f"Processing with {service} model"
                        }
                    )

                    # Process image with this service
                    service_result = await asyncio.to_thread(
                        processor.process_image,
                        file_name=unique_filename, 
                        image_path=file_path, 
                        model_type=service
                    )
                    results[ModelTypeEnum(service.upper())] = service_result
                    output_paths.append(service_result.get('output_path'))

                    # Update progress for completed service
                    current_progress += progress_per_service / 2
                    
                    # Refresh connection TTL periodically during long-running operations
                    await connection_manager.refresh_connection(client_id)

                local_file_tracker.add_file(file_path)
                img_properties = await cls.get_image_properties(file_path)

                # Send progress update
                await connection_manager.send_message(
                    client_id=client_id,
                    message={
                        "type": WebSocketMessageType.PROGRESS,
                        "task_id": task_id,
                        "progress": 80,
                        "message": "Processing complete, storing results"
                    }
                )

                # Construct metadata
                img_metadata = ImageMetadata(
                    extension=file_details["extension"],
                    mime_type=file_details["mime_type"],
                    file_type=file_details["file_type"],
                    file_size=file_details["file_size"],
                    width=img_properties["width"],
                    height=img_properties["height"],
                )

                # Store image_details, detection_results and processed_images in DB and AWS_S3
                img_data = CreateImage(
                    filename=unique_filename,
                    image_metadata=img_metadata,
                    local_file_path=str(file_path),
                )

                await connection_manager.send_message(
                    client_id=client_id,
                    message={
                        "type": WebSocketMessageType.PROGRESS,
                        "task_id": task_id,
                        "progress": 90,
                        "message": "Saving results to database and cloud storage"
                    }
                )

                # Refresh connection before triggering asynchronous task
                await connection_manager.refresh_connection(client_id)

                store_image_data_task.delay(
                    user_id=user_data.id,
                    username=user_data.username,
                    image_data=img_data.model_dump(),
                    services=services_to_run,
                    detection_data=results,
                )

                data = { **img_data.model_dump(), "results": results }

                await connection_manager.send_message(
                    client_id=client_id,
                    message={
                        "type": WebSocketMessageType.RESULT,
                        "task_id": task_id,
                        "status": "completed",
                        "progress": 100,
                        "message": "Processing complete",
                        "data": data
                    }
                )
                return data
            
            except Exception as e:
                log.error(f"Unexpected error in detection_processor_block: {str(e)}")
                raise

            finally:
                YOLOProcessorSingleton.release_task(task_id)
        
        except Exception as e:
            log.error(f"Unexpected error occurred in image detection: {str(e)}")        
            try:
                await connection_manager.send_message(
                    client_id=client_id,
                    message={
                        "type": WebSocketMessageType.ERROR,
                        "task_id": task_id,
                        "message": f"Image detection failed: {str(e)}"
                    }
                )
            except Exception as ws_err:
                log.error(f"Failed to send error notification via WebSocket: {str(ws_err)}")
                
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Image detection failed: {str(e)}"
            )