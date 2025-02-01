from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.password_service import PasswordService
from app.schemas.user_schema import UserCreate, UserRole
from app.db.models.user_model import User


class UserRepository:
    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate) -> User:
        """Create a new user in the database."""
        hashed_password = PasswordService.get_password_hash(user.password)

        user_data: Dict[str, Any] = {
            "email": user.email,
            "password": hashed_password,
            "role": UserRole.USER.value,
            "is_active": True,
            "is_blocked": False
        }
        
        # Dynamically add optional fields if they exist
        if hasattr(user, 'name') and user.name:
            user_data["name"] = user.name
        if hasattr(user, 'username') and user.username:
            user_data["username"] = user.username

        # Create user instance with dynamic fields
        db_user = User(**user_data)

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        return db_user        
