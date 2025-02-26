from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import db_session_manager
from app.configuration.config import settings
from app.services.auth_service import AuthService
from app.services.address_service import AddressService
from app.schemas.address_schema import AddressCreate, AddressUpdate, AddressResponse

from app.docs.descriptions import address_desc
from app.docs.responses import address_res

router = APIRouter()


@router.get(
    "/", 
    response_model=List[AddressResponse],
    status_code=status.HTTP_200_OK,
    responses=address_res.GET_ALL_ADDRESS_RESPONSES,
    summary="Get all addresses",
    description=address_desc.GET_ALL_ADDRESSES_DESCRIPTION
)
async def get_all_address(
    page: int =settings.DEFAULT_PAGE,
    limit: int = settings.DEFAULT_PAGE_LIMIT,
    db: AsyncSession = Depends(db_session_manager.get_db),
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
):
    """Retrieves all the addresses."""
    if not auth_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    return await AddressService.get_all_addresses(db, page, limit)


@router.get(
    "/{user_id}", 
    response_model=List[AddressResponse],
    status_code=status.HTTP_200_OK,
    responses=address_res.GET_ALL_ADDRESSES_OF_USER_RESPONSES,
    summary="Get all address of a user",
    description=address_desc.GET_USER_ADDRESSES_DESCRIPTION
)
async def get_all_addresses_of_user(
    user_id: int,
    page: int =settings.DEFAULT_PAGE,
    limit: int = settings.DEFAULT_PAGE_LIMIT,
    db: AsyncSession = Depends(db_session_manager.get_db),
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
):
    """Retrieves all the addresses of a user by user Id."""
    if not auth_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    return await AddressService.get_addresses_by_user_id(db, user_id, page, limit)


@router.post(
    "/create", 
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
    responses=address_res.CREATE_NEW_ADDRESS_RESPONSES,
    summary="Create New Address",
    description=address_desc.CREATE_ADDRESS_DESCRIPTION
)
async def create_new_address(
    address_body: AddressCreate,
    db: AsyncSession = Depends(db_session_manager.get_db),
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
):
    """Creates a new address for the current user."""
    if not auth_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    return await AddressService.create_address(db, auth_obj["user_id"], address_body)


@router.put(
    "/update/{address_id}", 
    response_model=AddressResponse,
    status_code=status.HTTP_200_OK,
    responses=address_res.UPDATE_ADDRESS_RESPONSES,
    summary="Update Existing Address",
    description=address_desc.UPDATE_ADDRESS_DESCRIPTION
)
async def update_address(
    address_id: int,
    address_body: AddressUpdate,
    db: AsyncSession = Depends(db_session_manager.get_db),
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
):
    """Updates an existing address for the current user."""
    if not auth_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    return await AddressService.update_address(
        db, auth_obj["user_id"], address_id, address_body
    )


@router.delete(
    "/delete/{address_id}", 
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    responses=address_res.DELETE_ADDRESS_RESPONSES,
    summary="Delete Existing Address",
    description=address_desc.DELETE_ADDRESS_DESCRIPTION
)
async def delete_address(
    address_id: int,
    db: AsyncSession = Depends(db_session_manager.get_db),
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
):
    """Deletes an existing address for the current user."""
    if not auth_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    await AddressService.delete_address(db, auth_obj["user_id"], address_id)
    return {"message": "Address deleted successfully"}
