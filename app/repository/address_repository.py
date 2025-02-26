from typing import List, Optional
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from app.configuration.config import settings
from app.db.models.address_model import Address
from app.schemas.address_schema import AddressCreate
from app.utils.logger import log


class AddressRepository:
    """Handles database operations for the Address model."""

    @staticmethod
    async def get_all_addresses(
        db: AsyncSession,
        offset: int = settings.DEFAULT_OFFSET,
        limit: int = settings.DEFAULT_PAGE_LIMIT,
    ) -> List[Address]:
        """
        Retrieve all addresses with pagination support.

        Args:
            db: Database session
            offset: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Address objects ordered by creation date (newest first)

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            query = (
                select(Address)
                .offset(offset)
                .limit(limit)
                .order_by(desc(Address.created_at))
            )
            result = await db.execute(query)
            return result.scalars().all()

        except SQLAlchemyError as db_err:
            log.critical(f"Database error in get_all_addresses: {db_err}")
            raise

        except Exception as e:
            log.critical(f"Unexpected error in get_all_addresses: {e}")
            raise

    @staticmethod
    async def get_addresses_by_user(
        db: AsyncSession,
        user_id: int,
        offset: int = settings.DEFAULT_OFFSET,
        limit: int = settings.DEFAULT_PAGE_LIMIT,
    ) -> List[Address]:
        """
        Retrieve all addresses for a specific user with pagination.

        Args:
            db: Database session
            user_id: ID of the user whose addresses to retrieve
            offset: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Address objects for the specified user

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            query = (
                select(Address)
                .where(Address.user_id == user_id)
                .offset(offset)
                .limit(limit)
                .order_by(desc(Address.created_at))
            )
            result = await db.execute(query)
            return result.scalars().all()

        except SQLAlchemyError as db_err:
            log.critical(f"Database error in get_addresses_by_user: {db_err}")
            raise

        except Exception as e:
            log.critical(f"Unexpected error in get_addresses_by_user: {e}")
            raise

    @staticmethod
    async def get_address_by_id(db: AsyncSession, address_id: int) -> Optional[Address]:
        """
        Retrieve a single address by its ID.

        Args:
            db: Database session
            address_id: ID of the address to retrieve

        Returns:
            Address object if found, None otherwise

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            query = select(Address).where(Address.id == address_id)
            result = await db.execute(query)
            return result.scalar_one_or_none()

        except SQLAlchemyError as db_err:
            log.critical(f"Database error in get_address_by_id: {db_err}")
            raise

        except Exception as e:
            log.critical(f"Unexpected error in get_address_by_id: {e}")
            raise

    @staticmethod
    async def create_address(db: AsyncSession, address_data: AddressCreate) -> Address:
        """
        Create a new address record.

        Args:
            db: Database session
            address_data: Pydantic model containing the address data

        Returns:
            Newly created Address object

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            new_address = Address(**address_data.model_dump())
            db.add(new_address)

            await db.commit()
            await db.refresh(new_address)
            return new_address

        except SQLAlchemyError as db_err:
            log.critical(f"Database error in create_address: {db_err}")
            raise

        except Exception as e:
            log.critical(f"Unexpected error in create_address: {e}")
            raise

    @staticmethod
    async def update_address(db: AsyncSession, address: Address) -> Address:
        """
        Update an existing address record.

        Args:
            db: Database session
            address: Address object with updated fields

        Returns:
            Updated Address object

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            await db.commit()
            await db.refresh(address)
            return address

        except SQLAlchemyError as db_err:
            log.critical(f"Database error in update_address: {db_err}")
            raise

        except Exception as e:
            log.critical(f"Unexpected error in update_address: {e}")
            raise

    @staticmethod
    async def delete_address(db: AsyncSession, address: Address) -> None:
        """
        Delete an address record.

        Args:
            db: Database session
            address: Address object to delete

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            await db.delete(address)
            await db.commit()

        except SQLAlchemyError as db_err:
            log.critical(f"Database error in delete_address: {db_err}")
            raise

        except Exception as e:
            log.critical(f"Unexpected error in delete_address: {e}")
            raise
