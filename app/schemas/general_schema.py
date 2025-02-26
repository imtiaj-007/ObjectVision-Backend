from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


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