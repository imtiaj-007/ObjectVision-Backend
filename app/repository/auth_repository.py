from typing import Optional
from sqlmodel import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.user_model import User


class AuthRepository:
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User] | None:
        """Retrieve a user by user_id."""
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
        
        except SQLAlchemyError as e:
            print(f"Database error retrieving user details by id: {e}")
            raise

        except Exception as e:        
            print(f"Unexpected error in get_user_by_id: {e}")
            raise 

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User] | None:
        """Retrieve a user by username."""
        try:
            result = await db.execute(select(User).where(User.username == username))
            return result.scalar_one_or_none()
        
        except SQLAlchemyError as e:
            print(f"Database error retrieving user details by username: {e}")
            raise

        except Exception as e:        
            print(f"Unexpected error in get_user_by_username: {e}")
            raise 

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User] | None:
        """Retrieve a user by email."""
        try:
            result = await db.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()
        
        except SQLAlchemyError as e:
            print(f"Database error retrieving user details by email: {e}")
            raise

        except Exception as e:        
            print(f"Unexpected error in get_user_by_email: {e}")
            raise  
    
    @staticmethod
    async def get_user_by_email_or_username(db: AsyncSession, user_key: str) -> Optional[User]:
        """Retrieve a user by email / username."""
        try:
            result = await db.execute(
                select(User)
                .where(
                    or_(
                        User.email == user_key,
                        User.username == user_key
                    )
                )
            )
            return result.scalar_one_or_none()
        
        except SQLAlchemyError as e:
            print(f"Database error retrieving user details: {e}")
            raise

        except Exception as e:        
            print(f"Unexpected error in get_user_by_email_or_username: {e}")
            raise