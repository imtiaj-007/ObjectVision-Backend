from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.enums import WebSocketMessageType


class SuccessResponse(BaseModel):
    status: Optional[int] = Field(
        None,
        example=1,
        description="Status like 0, 1."        
    )
    message: Optional[str] = Field(
        None,
        example="User Login success.",
        description="Message for the operation success."
    )
    extra_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        example={"user_id": 123, "role": "admin"},
        description="Additional dynamic fields."
    )


class WebSocketMessage(BaseModel):
    type: WebSocketMessageType
    data: Dict[str, Any]
    task_id: str
    service: Optional[str] = None
    progress: Optional[float] = None
    message: Optional[str] = None


class PresignedUrlRequest(BaseModel):
    file_path: str
    expiry_minutes: Optional[int] = None

class PresignedUrlResponse(BaseModel):
    url: str
    file_path: str
    expires_at: datetime