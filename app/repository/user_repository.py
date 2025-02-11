from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import update

from app.db.models.user_model import User
from app.schemas.user_schema import UserUpdate
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
        
        except SQLAlchemyError as db_err:
            log.critical(f"Unexpected error in create_user: {db_err}")
            raise 
        
        except Exception as e:
            log.critical(f"Unexpected error in create_user: {e}")
            raise 


    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, payload: Dict[str, Any]) -> User:
        """Update an existing user in the database."""     
        try:
            validated_data = UserUpdate.model_validate(payload)
            data_dict = validated_data.model_dump(exclude_unset=True)

            statement = (
                update(User)
                .where(User.id == user_id)
                .values(**data_dict)
            )
            result = await db.execute(statement)
            await db.commit()            

            return result.rowcount
        
        except SQLAlchemyError as db_err:
            log.critical(f"Unexpected error in update_user: {db_err}")
            raise 
        
        except Exception as e:
            log.error(f"Unexpected error in update_user: {e}")
            raise   
