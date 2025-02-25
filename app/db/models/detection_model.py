from pydantic import ConfigDict
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, JSON
from datetime import datetime, timezone
from typing import Union, List, Optional, TYPE_CHECKING
from app.db.database import Base
from app.schemas.detection_schema import (
    ModelTypeEnum,
    DetectionPrediction,
    SegmentationPrediction,
    ClassificationPrediction,
    PosePrediction,
)

if TYPE_CHECKING:
    from app.db.models.image_model import Image
    from app.db.models.processed_image_model import ProcessedImage


class Detection(Base, table=True):
    """Stores detected objects in images."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "image_id": 7,
                "parent_image_id": 1,
                "model_type": "detection",
                "processing_time": 2.29,
                "model_size": "medium_models",
                "confidence_threshold": 0.25,
                "device": "cuda",
                "predictions": [
                    {
                        "class_name": "apple",
                        "confidence": 0.95,
                        "bbox": [104, 15, 181, 90],
                    }
                ],
                "total_objects": 3,
                "processed_at": "2025-02-15T10:05:00Z",
            }
        },
    )

    __tablename__ = "detections"
    __table_args__ = {"schema": None, "keep_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    processed_image_id: int = Field(
        foreign_key="processed_images.id",
        ondelete="CASCADE",
        index=True,
        description="Reference to the processed image",
    )
    parent_image_id: int = Field(
        foreign_key="images.id",
        ondelete="CASCADE",
        index=True,
        description="Reference to the original image",
    )
    model_type: ModelTypeEnum = Field(
        ...,
        description="Type of model used (e.g., detection, segmentation)",
    )
    processing_time: float = Field(..., description="Time taken to process the image")
    model_size: str = Field(
        ...,
        max_length=50,
        description="Size of the model used (e.g., small, medium, large)",
    )
    confidence_threshold: float = Field(
        ..., description="Confidence threshold used for predictions"
    )
    device: str = Field(
        ..., max_length=50, description="Device used for processing (e.g., cpu, cuda)"
    )
    predictions: List[
        Union[
            DetectionPrediction,
            SegmentationPrediction,
            ClassificationPrediction,
            PosePrediction,
        ]
    ] = Field(..., sa_type=JSON, description="Predictions data (varies by model_type)")
    total_objects: int = Field(..., description="Total number of objects detected")
    processed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        index=True,
        nullable=False,
        description="Detection timestamp",
    )

    # Relationships
    image: "Image" = Relationship(back_populates="detections")  # One-to-Many relationship (Image → Detections)
    processed_image: Optional["ProcessedImage"] = Relationship(back_populates="detection") # One-to-One relationship (Processed Image → Detection)
