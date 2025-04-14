from pydantic import BaseModel
from sqlmodel import Field
from typing import List, Optional, Union, Dict, Any
from app.schemas.enums import ModelTypeEnum, ModelSizeEnum
from app.schemas.image_schema import ImageResponse
from app.helpers.partial_model import create_partial_model


class GeneralFields(BaseModel):
    """Model for detection predictions."""

    class_name: str  # banana, apple, orange
    confidence: float  # 0.97


class DetectionPrediction(GeneralFields):
    """Model for detection predictions."""

    bbox: List[float]  # [x_min, y_min, x_max, y_max]


class SegmentationPrediction(DetectionPrediction):
    """Model for segmentation predictions."""

    segmentation_mask: Optional[List[List[float]]]  # Optional mask data


class ClassificationPrediction(BaseModel):
    """Model for classification predictions."""

    primary_class: GeneralFields  # {"name": "banana", "confidence": 0.95}
    top_5_predictions: List[
        GeneralFields
    ]  # [{"name": "banana", "confidence": 0.95}, ...]


class PosePrediction(DetectionPrediction):
    """Model for pose predictions."""

    keypoints: List[List[float]]  # List of keypoints with coordinates and confidence


class DetectionRequest(BaseModel):
    model_size: ModelSizeEnum = Field(
        ModelSizeEnum.SMALL,
        description="Model size, representing YOLO pre-trained models.",
    )
    requested_services: List[str] = Field(
        None,
        description="Operations to perform on the image, e.g., detection, classification, etc.",
    )


class DetectionData(BaseModel):
    processed_image_id: int = Field(
        ...,
        description="Reference to the processed image",
    )
    parent_image_id: int = Field(
        ...,
        description="Reference to the original image",
    )
    model_type: ModelTypeEnum = Field(
        ...,
        description="Type of model used (e.g., detection, segmentation)",
    )
    processing_time: float = Field(..., description="Time taken to process the image")
    model_size: str = Field(
        ...,
        description="Size of the model used (e.g., small, medium, large)",
    )
    confidence_threshold: float = Field(
        ..., description="Confidence threshold used for predictions"
    )
    device: str = Field(..., description="Device used for processing (e.g., cpu, cuda)")
    predictions: List[
        Union[
            DetectionPrediction,
            SegmentationPrediction,
            ClassificationPrediction,
            PosePrediction,
        ]
    ] = Field(..., description="Predictions data (varies by model_type)")
    total_objects: int = Field(..., description="Total number of objects detected")
    output_path: Optional[str] = Field(None, description="Local / Cloud path of the processed file")


# Creating partial model instances to properly work with socket and DB data
PartialImageData = create_partial_model(ImageResponse)
PartialDetectionData = create_partial_model(DetectionData)


class DetectionResults(PartialImageData):
    results: Dict[ModelTypeEnum, Any] = Field(
        ..., description="Object of different types of detection results."
    )

    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    def model_validator(cls, values):
        results = values.get("results", {})
        for key, value in results.items():
            if not isinstance(value, PartialDetectionData):
                raise ValueError(
                    f"Expected PartialDetectionData for {key}, got {type(value)}"
                )
        return values


class DetectionWithCount(BaseModel):
    data: List[DetectionResults] = Field(
        ..., description="List of Detection results."
    )
    total_count: int = Field(
        default=0, description="Count of total predictions."
    )