from sqlmodel import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any

from app.db.models.image_model import Image
from app.db.models.detection_model import Detection
from app.db.models.processed_image_model import ProcessedImage
from app.utils.logger import log


class DetectionRepository:
    @staticmethod
    async def store_image_details(db: AsyncSession, image_data: Dict[str, Any]):
        try:
            image = Image(**image_data)              
            db.add(image)
            await db.commit()
            await db.refresh(image)
            return image

        except SQLAlchemyError as e:
            log.error(f"Database error storing image details: {e}")
            raise

        except Exception as e:
            log.error(f"Unexpected error in store_image_details: {e}")
            raise

    @staticmethod
    async def update_image_details(db: AsyncSession, image_id: int, **kwargs):
        try:
            stmt = update(Image).where(Image.id == image_id).values(**kwargs)
            await db.execute(stmt)
            await db.commit()

        except SQLAlchemyError as e:
            await db.rollback()
            log.error(f"Database error updating image details: {e}")
            raise

        except Exception as e:
            log.error(f"Unexpected error in update_image_details: {e}")
            raise
    
    @staticmethod
    async def store_processed_image_details(
        db: AsyncSession, processed_data: Dict[str, Any]
    ):
        try:
            processed_image = ProcessedImage(**processed_data)
            db.add(processed_image)
            await db.commit()
            await db.refresh(processed_image)
            return processed_image

        except SQLAlchemyError as e:
            await db.rollback()
            log.error(f"Database error storing processed image details: {e}")
            raise

        except Exception as e:
            log.error(f"Unexpected error in store_processed_image_details: {e}")
            raise

    @staticmethod
    async def update_processed_image_details(
        db: AsyncSession, processed_id: int, **kwargs
    ):
        try:
            stmt = (
                update(ProcessedImage)
                .where(ProcessedImage.id == processed_id)
                .values(**kwargs)
            )
            await db.execute(stmt)
            await db.commit()

        except SQLAlchemyError as e:
            await db.rollback()
            log.error(f"Database error updating processed image details: {e}")
            raise

        except Exception as e:
            log.error(f"Unexpected error in update_processed_image_details: {e}")
            raise

    @staticmethod
    async def store_detection_details(
        db: AsyncSession, detection_data: Dict[str, Any]
    ):
        try:
            detection = Detection(**detection_data)
            db.add(detection)
            await db.commit()
            await db.refresh(detection)
            return detection

        except SQLAlchemyError as e:
            await db.rollback()
            log.error(f"Database error storing detection details: {e}")
            raise

        except Exception as e:
            log.error(f"Unexpected error in store_detection_details: {e}")
            raise
