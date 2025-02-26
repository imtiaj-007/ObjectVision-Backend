from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import db_session_manager
from app.configuration.config import settings
from app.services.auth_service import AuthService
from app.services.phone_number_service import PhoneService
from app.schemas.phone_schema import PhoneNumberCreate, PhoneNumberUpdate, PhoneNumberResponse
from app.schemas.general_schema import SuccessResponse

from app.docs.descriptions import phone_desc
from app.docs.responses import phone_res

router = APIRouter()


@router.get(
    "/", 
    response_model=List[PhoneNumberResponse],
    status_code=status.HTTP_200_OK,
    responses=phone_res.GET_ALL_PHONES_RESPONSES,
    summary="Get All Phone Numbers",
    description=phone_desc.GET_ALL_PHONES_DESCRIPTION
)
async def get_all_phones(
    page: int = settings.DEFAULT_PAGE,
    limit: int = settings.DEFAULT_PAGE_LIMIT,
    db: AsyncSession = Depends(db_session_manager.get_db),
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
):
    """Retrieves all phone numbers."""
    if not auth_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    return await PhoneService.fetch_all_phones(db, page, limit)


@router.get(
    "/{user_id}", 
    response_model=List[PhoneNumberResponse],
    status_code=status.HTTP_200_OK,
    responses=phone_res.GET_ALL_PHONES_OF_USER_RESPONSES,
    summary="Get All Phone Numbers of a User",
    description=phone_desc.GET_ALL_PHONES_OF_USER_DESCRIPTION
)
async def get_all_phones_of_user(
    user_id: int,
    page: int = settings.DEFAULT_PAGE,
    limit: int = settings.DEFAULT_PAGE_LIMIT,
    db: AsyncSession = Depends(db_session_manager.get_db),
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
):
    """Retrieves all phone numbers of a user by user ID."""
    if not auth_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    return await PhoneService.fetch_user_phones(db, user_id, page, limit)


@router.post(
    "/create", 
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    responses=phone_res.CREATE_NEW_PHONE_RESPONSES,
    summary="Create New Phone Number",
    description=phone_desc.CREATE_NEW_PHONE_DESCRIPTION
)
async def create_new_phone(
    phone_body: PhoneNumberCreate,
    db: AsyncSession = Depends(db_session_manager.get_db),
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
):
    """Creates a new phone number for the current user."""
    if not auth_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    await PhoneService.create_new_phone(db, auth_obj["user_id"], phone_body)
    return {"message": "New phone number created successfully."}


@router.put(
    "/update/{phone_id}", 
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    responses=phone_res.UPDATE_PHONE_RESPONSES,
    summary="Update Existing Phone Number",
    description=phone_desc.UPDATE_PHONE_DESCRIPTION
)
async def update_phone(
    phone_id: int,
    phone_body: PhoneNumberUpdate,
    db: AsyncSession = Depends(db_session_manager.get_db),
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
):
    """Updates an existing phone number for the current user."""
    if not auth_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    await PhoneService.update_existing_phone(
        db, auth_obj["user_id"], phone_id, phone_body
    )
    return {"message": "Phone number updated successfully."}


@router.delete(
    "/delete/{phone_id}", 
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    responses=phone_res.DELETE_PHONE_RESPONSES,
    summary="Delete Existing Phone Number",
    description=phone_desc.DELETE_PHONE_DESCRIPTION
)
async def delete_phone(
    phone_id: int,
    db: AsyncSession = Depends(db_session_manager.get_db),
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
):
    """Deletes an existing phone number for the current user."""
    if not auth_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    await PhoneService.delete_existing_phone(db, auth_obj["user_id"], phone_id)
    return {"message": "Phone number deleted successfully."}