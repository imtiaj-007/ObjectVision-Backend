from sqlmodel import select, update, func, desc, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

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

        except Exception as e:
            log.error(f"Unexpected error in store_image_details: {str(e)}")
            raise

    @staticmethod
    async def update_image_details(db: AsyncSession, image_id: int, **kwargs):
        try:
            stmt = update(Image).where(Image.id == image_id).values(**kwargs)
            await db.execute(stmt)
            await db.commit()

        except Exception as e:
            log.error(f"Unexpected error in update_image_details: {str(e)}")
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

        except Exception as e:
            log.error(f"Unexpected error in store_processed_image_details: {str(e)}")
            raise

    @staticmethod
    async def update_processed_image_details(
        db: AsyncSession, processed_id: int, **kwargs
    ):
        try:
            statement = (
                update(ProcessedImage)
                .where(ProcessedImage.id == processed_id)
                .values(**kwargs)
            )
            await db.execute(statement)
            await db.commit()

        except Exception as e:
            log.error(f"Unexpected error in update_processed_image_details: {str(e)}")
            raise

    @staticmethod
    async def store_detection_details(db: AsyncSession, detection_data: Dict[str, Any]):
        try:
            detection = Detection(**detection_data)
            db.add(detection)
            await db.commit()
            await db.refresh(detection)
            return detection

        except Exception as e:
            log.error(f"Unexpected error in store_detection_details: {str(e)}")
            raise

    @staticmethod
    async def get_detection_details(
        db: AsyncSession,
        limit: int,
        offset: int,
        user_id: int,
        image_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        try:
            count_query = (
                select(func.count(distinct(Image.id)))
                .where(Image.user_id == user_id)
                .join(Detection, Image.id == Detection.parent_image_id)
            )
            count_result = await db.execute(count_query)
            total_count = count_result.scalar_one()

            image_query = (
                select(Image.id)
                .where(Image.user_id == user_id)
                .join(Detection, Image.id == Detection.parent_image_id)
                .group_by(Image.id)
                .order_by(desc(func.max(Detection.processed_at)))
            )
            
            if image_id is not None:
                image_query = image_query.where(Image.id == image_id)
            else:
                image_query = image_query.limit(limit).offset(offset)
            
            image_result = await db.execute(image_query)
            image_ids = [row[0] for row in image_result.all()]

            result_dict = {"data": [], "total_count": total_count}
            
            if not image_ids:
                return result_dict
            
            images_query = select(Image).where(Image.id.in_(image_ids))
            images_result = await db.execute(images_query)
            images = {image.id: image for image in images_result.scalars().all()}
            
            detections_query = (
                select(Detection)
                .where(Detection.parent_image_id.in_(image_ids))
                .order_by(Detection.processed_at.desc())
            )
            detections_result = await db.execute(detections_query)
            detections = detections_result.scalars().all()
            
            detection_groups = {}
            for detection in detections:
                if detection.parent_image_id not in detection_groups:
                    detection_groups[detection.parent_image_id] = {}

                detection_dict = {
                    column.name: getattr(detection, column.name)
                    for column in detection.__table__.columns
                }
                detection_groups[detection.parent_image_id][detection.model_type.value] = detection_dict
            
            processed_results = []
            for image_id in image_ids:
                if image_id in images:
                    image = images[image_id]
                    image_dict = {
                        column.name: getattr(image, column.name)
                        for column in image.__table__.columns
                    }
                    image_dict["results"] = detection_groups.get(image_id, {})
                    processed_results.append(image_dict)
            
            result_dict["data"] = processed_results
            return result_dict
                
        except Exception as e:
            log.error(f"Unexpected error in get_detection_details: {str(e)}")
            raise