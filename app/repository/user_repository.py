from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.configuration.security import SecurityConfig
from app.models.user_model import UserCreate
from app.db.schemas.user_schema import User, UserRole


class UserRepository:
    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate) -> User:
        """Create a new user in the database."""
        hashed_password = SecurityConfig.get_password_hash(user.password)

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
