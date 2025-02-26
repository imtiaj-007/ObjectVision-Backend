from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repository.address_repository import AddressRepository
from app.db.models.address_model import Address
from app.schemas.address_schema import AddressCreate, AddressUpdate


class AddressService:
    """Handles address-related business logic."""

    @staticmethod
    async def fetch_all_addresses(
        db: AsyncSession, page: int, limit: int
    ) -> List[Address]:
        """
        Retrieve all addresses with pagination support.

        Args:
            db: Database session
            page: Page number (1-based)
            limit: Number of items per page

        Returns:
            List of Address objects for the requested page
        """
        offset = (page - 1) * limit
        return await AddressRepository.get_all_addresses(db, offset, limit)

    @staticmethod
    async def fetch_user_addresses(
        db: AsyncSession, user_id: int, page: int, limit: int
    ) -> List[Address]:
        """
        Retrieve all addresses for a specific user with pagination.

        Args:
            db: Database session
            user_id: ID of the user whose addresses to retrieve
            page: Page number (1-based)
            limit: Number of items per page

        Returns:
            List of Address objects for the specified user
        """
        offset = (page - 1) * limit
        return await AddressRepository.get_addresses_by_user(db, user_id, offset, limit)

    @staticmethod
    async def create_new_address(
        db: AsyncSession, user_id: int, address_data: AddressCreate
    ) -> Address:
        """
        Create a new address for a user.

        Args:
            db: Database session
            user_id: ID of the user creating the address
            address_data: Pydantic model containing the address data

        Returns:
            Newly created Address object
        """
        address_data.user_id = user_id
        return await AddressRepository.create_address(db, address_data)

    @staticmethod
    async def update_existing_address(
        db: AsyncSession, user_id: int, address_id: int, update_data: AddressUpdate
    ) -> Address:
        """
        Update an existing address if the user has permission.

        Args:
            db: Database session
            user_id: ID of the user attempting the update
            address_id: ID of the address to update
            update_data: Pydantic model containing the updated fields

        Returns:
            Updated Address object

        Raises:
            HTTPException: If address not found or user not authorized
        """
        address = await AddressRepository.get_address_by_id(db, address_id)
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Address not found."
            )
        if address.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this address.",
            )

        valid_fields = update_data.model_dump(exclude_unset=True)
        for key, value in valid_fields.items():
            if hasattr(address, key):
                setattr(address, key, value)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid field: {key}",
                )

        return await AddressRepository.update_address(db, address)

    @staticmethod
    async def delete_existing_address(
        db: AsyncSession, user_id: int, address_id: int
    ) -> None:
        """
        Delete an address if the user has permission.

        Args:
            db: Database session
            user_id: ID of the user attempting the deletion
            address_id: ID of the address to delete

        Raises:
            HTTPException: If address not found or user not authorized
        """
        address = await AddressRepository.get_address_by_id(db, address_id)
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Address not found."
            )
        if address.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this address.",
            )
        await AddressRepository.delete_address(db, address)
