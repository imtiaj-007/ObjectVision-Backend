from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.enums import ModelTypeEnum


class ImageMetadata(BaseModel):
    extension: str = Field(..., description="File extension, e.g., jpg, png")
    mime_type: str = Field(..., description="MIME type of the file")
    file_type: str = Field(..., description="Type of the file, e.g., IMAGE")
    file_size: Optional[int] = Field(
        None, description="Size of the image file in bytes"
    )
    width: Optional[int] = Field(None, description="Width of the image in pixels")
    height: Optional[int] = Field(None, description="Height of the image in pixels")


class CreateImage(BaseModel):
    user_id: Optional[int] = Field(default=None, description="Uploader's user ID")
    filename: str = Field(
        ..., max_length=255, description="Original filename of the image"
    )
    image_metadata: ImageMetadata = Field(
        ..., description="Metadata about the image file"
    )
    local_file_path: str = Field(
        ..., description="Path to stored image on local server"
    )    


class UpdateImage(BaseModel):
    cloud_file_path: Optional[str] = Field(
        None, description="Path to stored image in cloud storage"
    )
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp when image was last updated"
    )
    processed: Optional[bool] = Field(
        default=False, description="Indicates if YOLO processing has been applied"
    )


class UpdateProcessedImage(BaseModel):
    cloud_processed_path: Optional[str] = Field(
        None, description="Path to the processed image in aws_s3"
    )
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp when image was last updated"
    )
    

class ProcessedImageData(BaseModel):
    original_image_id: int = Field(
        ..., description="Reference to the original image",
    )
    local_processed_path: str = Field(
        ..., description="Path to the processed image in local server"
    )
    processed_type: ModelTypeEnum = Field(
        ..., description="Processing type (detection, segmentation, classification etc.)",
    )


# Combined Image Response Model    
class ImageResponse(CreateImage, UpdateImage):
    id: int = Field(..., description="Unique ID of image stored in DB")
    uploaded_at: Optional[datetime] = Field(
        None, description="Timestamp when image was uploaded"
    )
