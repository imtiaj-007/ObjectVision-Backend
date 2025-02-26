from typing import List, Optional
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from app.configuration.config import settings
from app.db.models.phone_number import PhoneNumber
from app.schemas.phone_schema import PhoneNumberCreate
from app.utils.logger import log


class PhoneRepository:
    """Handles database operations for the Phone model."""

    @staticmethod
    async def get_all_phones(
        db: AsyncSession,
        offset: int = settings.DEFAULT_OFFSET,
        limit: int = settings.DEFAULT_PAGE_LIMIT,
    ) -> List[PhoneNumber]:
        """
        Retrieve all phones with pagination support.

        Args:
            db: Database session
            offset: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Phone objects ordered by creation date (newest first)

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            query = (
                select(PhoneNumber)
                .offset(offset)
                .limit(limit)
                .order_by(desc(PhoneNumber.created_at))
            )
            result = await db.execute(query)
            return result.scalars().all()

        except SQLAlchemyError as db_err:
            log.critical(f"Database error in get_all_phones: {db_err}")
            raise

        except Exception as e:
            log.critical(f"Unexpected error in get_all_phones: {e}")
            raise

    @staticmethod
    async def get_phones_by_user(
        db: AsyncSession,
        user_id: int,
        offset: int = settings.DEFAULT_OFFSET,
        limit: int = settings.DEFAULT_PAGE_LIMIT,
    ) -> List[PhoneNumber]:
        """
        Retrieve all phones for a specific user with pagination.

        Args:
            db: Database session
            user_id: ID of the user whose phones to retrieve
            offset: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Phone objects for the specified user

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            query = (
                select(PhoneNumber)
                .where(PhoneNumber.user_id == user_id)
                .offset(offset)
                .limit(limit)
                .order_by(desc(PhoneNumber.created_at))
            )
            result = await db.execute(query)
            return result.scalars().all()

        except SQLAlchemyError as db_err:
            log.critical(f"Database error in get_phones_by_user: {db_err}")
            raise

        except Exception as e:
            log.critical(f"Unexpected error in get_phones_by_user: {e}")
            raise

    @staticmethod
    async def get_phone_by_id(db: AsyncSession, phone_id: int) -> Optional[PhoneNumber]:
        """
        Retrieve a single phone by its ID.

        Args:
            db: Database session
            phone_id: ID of the phone to retrieve

        Returns:
            Phone object if found, None otherwise

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            query = select(PhoneNumber).where(PhoneNumber.id == phone_id)
            result = await db.execute(query)
            return result.scalar_one_or_none()

        except SQLAlchemyError as db_err:
            log.critical(f"Database error in get_phone_by_id: {db_err}")
            raise

        except Exception as e:
            log.critical(f"Unexpected error in get_phone_by_id: {e}")
            raise

    @staticmethod
    async def create_phone(db: AsyncSession, phone_data: PhoneNumberCreate) -> PhoneNumber:
        """
        Create a new phone record.

        Args:
            db: Database session
            phone_data: Pydantic model containing the phone data

        Returns:
            Newly created Phone object

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            new_phone = PhoneNumber(**phone_data.model_dump())
            db.add(new_phone)

            await db.commit()
            await db.refresh(new_phone)
            return new_phone

        except SQLAlchemyError as db_err:
            log.critical(f"Database error in create_phone: {db_err}")
            raise

        except Exception as e:
            log.critical(f"Unexpected error in create_phone: {e}")
            raise

    @staticmethod
    async def update_phone(db: AsyncSession, phone: PhoneNumber) -> PhoneNumber:
        """
        Update an existing phone record.

        Args:
            db: Database session
            phone: Phone object with updated fields

        Returns:
            Updated Phone object

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            await db.commit()
            await db.refresh(phone)
            return phone

        except SQLAlchemyError as db_err:
            log.critical(f"Database error in update_phone: {db_err}")
            raise

        except Exception as e:
            log.critical(f"Unexpected error in update_phone: {e}")
            raise

    @staticmethod
    async def delete_phone(db: AsyncSession, phone: PhoneNumber) -> None:
        """
        Delete a phone record.

        Args:
            db: Database session
            phone: Phone object to delete

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            await db.delete(phone)
            await db.commit()

        except SQLAlchemyError as db_err:
            log.critical(f"Database error in delete_phone: {db_err}")
            raise

        except Exception as e:
            log.critical(f"Unexpected error in delete_phone: {e}")
            raise