from pydantic import BaseModel
from sqlmodel import Field
from typing import List, Optional, Union
from enum import Enum


class ModelTypeEnum(str, Enum):
    DETECTION = "DETECTION"
    SEGMENTATION = "SEGMENTATION"
    CLASSIFICATION = "CLASSIFICATION"
    POSE = "POSE"

class GeneralFields(BaseModel):
    """Model for detection predictions."""
    class_name: str         # banana, apple, orange
    confidence: float       # 0.97

class DetectionPrediction(GeneralFields):
    """Model for detection predictions."""    
    bbox: List[float]       # [x_min, y_min, x_max, y_max]


class SegmentationPrediction(DetectionPrediction):
    """Model for segmentation predictions."""
    segmentation_mask: Optional[List[List[float]]]  # Optional mask data


class ClassificationPrediction(BaseModel):
    """Model for classification predictions."""
    primary_class: GeneralFields            # {"name": "banana", "confidence": 0.95}
    top_5_predictions: List[GeneralFields]  # [{"name": "banana", "confidence": 0.95}, ...]


class PosePrediction(DetectionPrediction):
    """Model for pose predictions."""
    keypoints: List[List[float]]            # List of keypoints with coordinates and confidence


class DetectionData(BaseModel):
    processed_image_id: int = Field(
        ..., description="Reference to the processed image",
    )
    parent_image_id: int = Field(
        ..., description="Reference to the original image",
    )
    model_type: ModelTypeEnum = Field(
        ...,
        description="Type of model used (e.g., detection, segmentation)",
    )
    processing_time: float = Field(..., description="Time taken to process the image")
    model_size: str = Field(
        ..., description="Size of the model used (e.g., small, medium, large)",
    )
    confidence_threshold: float = Field(
        ..., description="Confidence threshold used for predictions"
    )
    device: str = Field(
        ..., description="Device used for processing (e.g., cpu, cuda)"
    )
    predictions: List[
        Union[
            DetectionPrediction,
            SegmentationPrediction,
            ClassificationPrediction,
            PosePrediction,
        ]
    ] = Field(..., description="Predictions data (varies by model_type)")
    total_objects: int = Field(..., description="Total number of objects detected")