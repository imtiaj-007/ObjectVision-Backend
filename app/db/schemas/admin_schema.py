from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

# User Management
class AdminUserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: str = Field(..., pattern='^(admin|moderator|analyst)$')
    is_active: bool = True

class AdminUserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, pattern='^(admin|moderator|analyst)$')
    is_active: Optional[bool] = None

# Model Management
class ModelConfig(BaseModel):
    name: str
    version: str
    confidence_threshold: float = Field(ge=0.0, le=1.0)
    input_size: Optional[List[int]] = None

# System Configuration
class SystemConfig(BaseModel):
    max_concurrent_detections: Optional[int] = Field(None, ge=1, le=100)
    storage_limit_gb: Optional[int] = Field(None, ge=10)
    log_retention_days: Optional[int] = Field(None, ge=1, le=365)