from typing import Optional, Literal
from pydantic import BaseModel, Field, StringConstraints
from typing_extensions import Annotated
from app.schemas.user_schema import UserRole


# List of available token types
TokenType = Literal["access_token", "refresh_token"]

# Access Token Format
class AccessToken(BaseModel):
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
    exp: Optional[int] = Field(
        None,
        example=1704067200,
        description="Token expiration timestamp (Unix epoch time)."
    )

# Refresh Token Format
class RefreshToken(AccessToken):
    ip_address: Optional[str] = Field(
        None,
        example="192.168.1.1",
        description="The IP address of the user when the refresh token was issued."
    )
    user_agent: Optional[str] = Field(
        None,
        example="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        description="The user agent string of the browser or client application."
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