from typing import Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.configuration.security import SecurityConfig
from app.models.user_model import UserCreate
from app.db.schemas.user_schema import User, UserRole


class UserRepository:
    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate) -> User:
        """Create a new user in the database."""
        hashed_password = SecurityConfig.get_password_hash(user.password)

        db_user = User(
            username=user.username,
            email=user.email,
            password=hashed_password,
            role=UserRole.USER.value,
            mobile=user.mobile,
            is_active=True,
            is_blocked=False,
        )

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        return db_user

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User] | None:
        """Retrieve a user by username."""
        try:
            result = await db.execute(select(User).where(User.username == username))
            return result.scalar_one_or_none()
        except Exception as e:
            print(f"Error retrieving user by username {username}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve user by username"
            )

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User] | None:
        """Retrieve a user by email."""
        try:
            result = await db.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()
        except Exception as e:
            print(f"Error retrieving user by email {email}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve user by email"
            )   
