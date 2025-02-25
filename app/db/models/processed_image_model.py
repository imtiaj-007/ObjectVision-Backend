from sqlalchemy import DateTime
from sqlmodel import Field, Relationship
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from app.schemas.detection_schema import ModelTypeEnum
from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.image_model import Image
    from app.db.models.detection_model import Detection


class ProcessedImage(Base, table=True):
    """
    Stores processed image versions (e.g., bounding boxes drawn, segmentation overlays).

    Example:
    {
        "id": 1,
        "original_image_id": 4,
        "local_processed_path": "/processed_images/example.jpg",
        "cloud_processed_path": "/processed_images/example.jpg",
        "processed_type": "detection",        
        "generated_at": "2025-02-15T10:10:00Z"
        "updated_at": "2025-02-15T10:13:00Z"
    }
    """

    __tablename__ = "processed_images"
    __table_args__ = {"schema": None, "keep_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    original_image_id: int = Field(
        foreign_key="images.id",
        ondelete="CASCADE",
        index=True,
        description="Reference to the original image",
    )
    local_processed_path: str = Field(
        ..., description="Path to the processed image in local server"
    )
    cloud_processed_path: Optional[str] = Field(
        None, description="Path to the processed image in aws_s3"
    )
    processed_type: ModelTypeEnum = Field(
        ...,
        index=True,
        description="Processing type (detection, segmentation, classification etc.)",
    )
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        index=True,
        nullable=False,
        description="Timestamp of processed image generation",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=True,
        description="Timestamp when image data was edited, like path URLs",
    )

    # Relationships
    image: "Image" = Relationship(  # One-to-Many relationship (Image → Processed Images)
        back_populates="processed_images",
        sa_relationship_kwargs={"lazy": "joined"}
    )  
    detection: Optional["Detection"] = Relationship(back_populates="processed_image") # One-to-One relationship (Detection → Processed Image)
