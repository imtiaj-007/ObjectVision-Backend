from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repository.phone_number_repository import PhoneRepository
from app.db.models.phone_number import PhoneNumber
from app.schemas.phone_schema import PhoneNumberCreate, PhoneNumberUpdate


class PhoneService:
    """Handles phone-related business logic."""

    @staticmethod
    async def fetch_all_phones(
        db: AsyncSession, page: int, limit: int
    ) -> List[PhoneNumber]:
        """
        Retrieve all phones with pagination support.

        Args:
            db: Database session
            page: Page number (1-based)
            limit: Number of items per page

        Returns:
            List of Phone objects for the requested page
        """
        offset = (page - 1) * limit
        return await PhoneRepository.get_all_phones(db, offset, limit)

    @staticmethod
    async def fetch_user_phones(
        db: AsyncSession, user_id: int, page: int, limit: int
    ) -> List[PhoneNumber]:
        """
        Retrieve all phones for a specific user with pagination.

        Args:
            db: Database session
            user_id: ID of the user whose phones to retrieve
            page: Page number (1-based)
            limit: Number of items per page

        Returns:
            List of Phone objects for the specified user
        """
        offset = (page - 1) * limit
        return await PhoneRepository.get_phones_by_user(db, user_id, offset, limit)

    @staticmethod
    async def create_new_phone(
        db: AsyncSession, user_id: int, phone_data: PhoneNumberCreate
    ) -> PhoneNumber:
        """
        Create a new phone for a user.

        Args:
            db: Database session
            user_id: ID of the user creating the phone
            phone_data: Pydantic model containing the phone data

        Returns:
            Newly created Phone object
        """
        phone_data.user_id = user_id
        return await PhoneRepository.create_phone(db, phone_data)

    @staticmethod
    async def update_existing_phone(
        db: AsyncSession, user_id: int, phone_id: int, update_data: PhoneNumberUpdate
    ) -> PhoneNumber:
        """
        Update an existing phone if the user has permission.

        Args:
            db: Database session
            user_id: ID of the user attempting the update
            phone_id: ID of the phone to update
            update_data: Pydantic model containing the updated fields

        Returns:
            Updated Phone object

        Raises:
            HTTPException: If phone not found or user not authorized
        """
        phone = await PhoneRepository.get_phone_by_id(db, phone_id)
        if not phone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Phone not found."
            )
        if phone.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this phone.",
            )

        valid_fields = update_data.model_dump(exclude_unset=True)
        for key, value in valid_fields.items():
            if hasattr(phone, key):
                setattr(phone, key, value)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid field: {key}",
                )

        return await PhoneRepository.update_phone(db, phone)

    @staticmethod
    async def delete_existing_phone(
        db: AsyncSession, user_id: int, phone_id: int
    ) -> None:
        """
        Delete a phone if the user has permission.

        Args:
            db: Database session
            user_id: ID of the user attempting the deletion
            phone_id: ID of the phone to delete

        Raises:
            HTTPException: If phone not found or user not authorized
        """
        phone = await PhoneRepository.get_phone_by_id(db, phone_id)
        if not phone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Phone not found."
            )
        if phone.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this phone.",
            )
        await PhoneRepository.delete_phone(db, phone)