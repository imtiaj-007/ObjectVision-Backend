from typing import Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.user_model import User
from app.utils.logger import log


class UserRepository:
    @staticmethod
    async def create_user(db: AsyncSession, user_data: Dict[str, Any]) -> User:
        """Create a new user in the database."""        
        try:
            # Validate user_data and store it
            db_user = User(**user_data)

            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)

            return db_user
        
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="A database error occurred."
            )
        
        except Exception as e:
            log.error(f"Unexpected error in create_user: {e}")
            raise   
