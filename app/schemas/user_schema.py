from typing import Optional
from pydantic import BaseModel, EmailStr, Field, StringConstraints
from typing_extensions import Annotated, List
from datetime import datetime
from app.schemas.address_schema import AddressBase, AddressResponse
from app.schemas.phone_schema import PhoneNumberBase, PhoneNumberResponse
from app.schemas.enums import UserRole


# Base User Model (Shared Fields)
class UserBase(BaseModel):
    name: Optional[Annotated[str, StringConstraints(min_length=3, max_length=50)]] = (
        Field(
            None,
            example="John Doe",
            description="Actual Name of the user (3-50 characters).",
        )
    )
    email: EmailStr = Field(
        ..., example="user@example.com", description="Valid email address of the user."
    )

    class Config:
        from_attributes = True


# Create User (Input for Creating Users)
class UserCreate(UserBase):
    password: Annotated[str, StringConstraints(min_length=8, max_length=64)] = Field(
        ...,
        example="securepassword",
        description="Password for the user (8-64 characters).",
    )


# User response upon user creation
class UserCreateResponse(BaseModel):
    status: int = Field(
        default=1, example=1, description="Status representing success/error."
    )
    message: str = Field(
        ...,
        example="User has been created successfully.",
        description="Message for user creation.",
    )


# Update User (Input for Updating Users)
class UserUpdate(BaseModel):
    username: Optional[
        Annotated[str, StringConstraints(min_length=3, max_length=15)]
    ] = Field(
        None,
        example="john_doe",
        description="Unique username for the user (3-15 characters).",
    )
    name: Optional[Annotated[str, StringConstraints(min_length=3, max_length=50)]] = (
        Field(
            None,
            example="John Doe",
            description="Actual Name of the user (3-50 characters).",
        )
    )
    role: Optional[UserRole] = Field(
        None,
        example=UserRole.USER.value,
        description="Role of the user (optional, mapped to a predefined set of roles).",
    )
    is_active: Optional[bool] = Field(
        None,
        example=True,
        description="Indicates if the user is currently active (optional).",
    )
    is_blocked: Optional[bool] = Field(
        None, example=False, description="Indicates if the user is blocked (optional)."
    )


# User Response for sending to frontend
class UserResponse(UserBase):
    id: int = Field(..., example=1, description="Unique identifier for the user.")
    username: Optional[
        Annotated[str, StringConstraints(min_length=3, max_length=15)]
    ] = Field(
        None,
        example="john_doe",
        description="Unique username for the user (3-15 characters).",
    )
    is_active: bool = Field(
        default=True,
        example=True,
        description="Indicates if the user is currently active.",
    )
    is_blocked: bool = Field(
        default=False, example=False, description="Indicates if the user is blocked."
    )
    role: UserRole = Field(
        default=UserRole.USER.value,
        example=UserRole.USER.value,
        description="Role of the user (mapped to a predefined set of roles).",
    )

    class Config:
        from_attributes = True


# User Data (For Internal Use)
class UserData(UserResponse):
    created_at: datetime = Field(
        None,
        example="2025-01-25T12:00:00Z",
        description="Timestamp when the user was created.",
    )
    updated_at: Optional[datetime] = Field(
        None,
        example="2025-01-26T12:00:00Z",
        description="Timestamp when the user was last updated (optional).",
    )

    class Config:
        from_attributes = True


# User Profile response
class UserProfile(BaseModel):
    user: UserResponse = Field(..., description="Comprehensive User Details")
    addresses: List[AddressResponse] = Field(
        default_factory=list, description="List of user addresses."
    )
    phone_numbers: List[PhoneNumberResponse] = Field(
        default_factory=list, description="List of user phone numbers."
    )
    # TODO: Subscription module needs to be implemented
    # subscription: Dict[str, Any] = Field(
    #     None,
    #     description="Active subscription details."
    # )


# Login Request (Input for Authentication)
class UserLogin(BaseModel):
    user_key: Annotated[
        EmailStr | str,
        Field(
            ...,
            examples=["user@example.com", "user123"],
            description="Email address or username for authentication.",
        ),
    ]
    password: Annotated[str, StringConstraints(min_length=8, max_length=64)] = Field(
        ...,
        example="securepassword",
        description="Password of the user for authentication.",
    )
    remember_me: bool = Field(
        False, description="Remember me option to keep the user Loggedin."
    )
    new_device: bool = Field(
        False,
        description="New device field specifies if user is trying to login from new_device.",
    )


# Logout Response
class LogoutResponse(BaseModel):
    message: str = Field(
        None,
        example="You have successfully logged out.",
        description="A message stating logout is successful.",
    )


# User Info / Basic user data
class UserInfo(BaseModel):
    username: Annotated[str, StringConstraints(min_length=3, max_length=15)] = Field(
        ...,
        example="john_doe",
        description="Unique username for the user (3-15 characters).",
    )
    phone_number: PhoneNumberBase = Field(
        ...,
        example={
            "phone_number": "1234567890",
            "country_code": "+91",
            "type": "HOME",
            "is_primary": True,
        },
        description="User's Phone Number Details.",
    )
    address: AddressBase = Field(
        ...,
        example={
            "address_line_1": "Apt 4B",
            "address_line_2": "123 Main St",
            "city": "Kolkata",
            "state_province": "West Bengal",
            "postal_code": "700000",
            "country": "India",
            "country_code": "IN",
            "latitude": "40.7128",
            "longitude": "-74.0060",
            "type": "HOME",
        },
        description="User's primary address.",
    )
