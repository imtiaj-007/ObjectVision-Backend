from pydantic import ConfigDict
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, JSON
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from app.db.database import Base
from app.schemas.image_schema import ImageMetadata

if TYPE_CHECKING:
    from app.db.models.user_model import User
    from app.db.models.detection_model import Detection
    from app.db.models.processed_image_model import ProcessedImage


class Image(Base, table=True):
    """Stores uploaded images and metadata."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 10,
                "filename": "example.jpg",
                "image_metadata": {
                    "extension": "jpg",
                    "mime_type": "image/jpeg",
                    "file_type": "IMAGE",
                    "file_size": "5MB",
                    "width": "1920px",
                    "height": "1080px"
                },
                "local_file_path": "/uploads/images/example.jpg",
                "cloud_file_path": "/uploads/images/example.jpg",
                "uploaded_at": "2025-02-15T10:00:00Z",
                "updated_at": "2025-02-15T10:07:00Z",
                "processed": False,
            }
        },
    )

    __tablename__ = "images"
    __table_args__ = {
        "schema": None, 
        "keep_existing": True
    }

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: Optional[int] = Field(
        default=None, foreign_key="users.id", description="Uploader's user ID"
    )
    filename: str = Field(
        ..., max_length=255, description="Original filename of the image"
    )
    image_metadata: ImageMetadata = Field(
        default=None, sa_type=JSON, description="Image metadata in JSON format"
    )
    local_file_path: str = Field(
        ..., description="Path to stored image in local server"
    )
    cloud_file_path: Optional[str] = Field(None, description="Path to stored image in aws_s3")
    uploaded_at: datetime = Field(
        default_factory=lambda:datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
        description="Timestamp when image was uploaded",
    )
    updated_at: datetime = Field(
        default_factory=lambda:datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=True,
        description="Timestamp when image data was edited, like path URLs",
    )
    processed: bool = Field(
        default=False, description="Indicates if YOLO processing has been applied"
    )

    # Relationships
    user: Optional["User"] = Relationship(  # One-to-Many relationship (User → Images)
        back_populates="images",
        sa_relationship_kwargs={"lazy": "joined"}
    )   
    detections: List["Detection"] = Relationship(back_populates="image")    # Many-to-One relationship (Detections → Image)
    processed_images: List["ProcessedImage"] = Relationship(back_populates="image") # Many-to-One relationship (Processed Images → Image)
