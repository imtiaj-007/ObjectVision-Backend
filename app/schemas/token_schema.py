from typing import Optional
from pydantic import BaseModel, Field, StringConstraints
from typing_extensions import Annotated
from app.schemas.user_schema import UserRole


# Token Data (Stored in Access Tokens)
class TokenData(BaseModel):
    sub: Optional[str] = Field(
        None,
        example="john_doe",
        description="Subject or username of the user."
    )
    user_id: Optional[int] = Field(
        None,
        example=1,
        description="Unique identifier of the user."
    )
    role: Optional[int] = Field(
        None,
        example=UserRole.USER.value,
        description="Role of the user (stored in the token)."
    )


# Access Token Response (Output for Token API)
class TokenResponse(BaseModel):
    access_token: Annotated[
        str,
        StringConstraints(min_length=20, max_length=500)
    ] = Field(
        ...,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        description="JWT access token for the user."
    )
    token_type: str = Field(
        ...,
        example="Bearer",
        description="Type of the token, typically 'Bearer'."
    )