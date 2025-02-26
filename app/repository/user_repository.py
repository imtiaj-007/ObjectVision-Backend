from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select, update

from app.db.models.user_model import User
from app.db.models.address_model import Address
from app.db.models.phone_number import PhoneNumber
from app.schemas.user_schema import UserUpdate, UserProfile, UserData
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
            log.critical(f"Database error in create_user: {db_err}")
            raise

        except Exception as e:
            log.critical(f"Unexpected error in create_user: {e}")
            raise

    @staticmethod
    async def update_user(
        db: AsyncSession, user_id: int, user_data: Dict[str, Any]
    ) -> User:
        """Update an existing user in the database."""
        try:
            validated_data = UserUpdate.model_validate(user_data)
            data_dict = validated_data.model_dump(exclude_unset=True)

            statement = update(User).where(User.id == user_id).values(**data_dict)
            result = await db.execute(statement)
            await db.commit()

            return result.rowcount

        except SQLAlchemyError as db_err:
            log.critical(f"Database error in update_user: {db_err}")
            raise

        except Exception as e:
            log.error(f"Unexpected error in update_user: {e}")
            raise


    @staticmethod
    async def get_profile(db: AsyncSession, user_id: int) -> Optional[UserProfile]:
        """Get profile information of user using user_id, including address and phone numbers as JSON aggregates."""
        try:            
            # JSON templates for aggregation
            user_fields = {
                col.name: getattr(User, col.name)
                for col in User.__table__.columns
            }

            address_template = {
                col.name: getattr(Address, col.name)
                for col in Address.__table__.columns
            }

            phone_template = {
                col.name: getattr(PhoneNumber, col.name)
                for col in PhoneNumber.__table__.columns
            }

            # Query statement
            statement = (
                select(
                    User,
                    func.coalesce(
                        func.json_agg(
                            func.json_build_object(
                                *[item for pair in address_template.items() for item in pair]
                            )
                        ).filter(Address.id.isnot(None)),
                        func.json_build_array()
                    ).label("addresses"),
                    func.coalesce(
                        func.json_agg(
                            func.json_build_object(
                                *[item for pair in phone_template.items() for item in pair]
                            )
                        ).filter(PhoneNumber.id.isnot(None)),
                        func.json_build_array()
                    ).label("phone_numbers")
                )
                .join(Address, Address.user_id == User.id, isouter=True)
                .join(PhoneNumber, PhoneNumber.user_id == User.id, isouter=True)
                .where(User.id == user_id)
                .group_by(User)
            )

            result = await db.execute(statement)
            row = result.mappings().first()

            if not row:
                return None

            # Convert row to UserProfile
            return UserProfile(
                user=dict(row["User"]),
                addresses=row["addresses"],
                phone_numbers=row["phone_numbers"]
            )

        except SQLAlchemyError as db_err:
            log.critical(f"Database error in get_profile: {db_err}")
            raise

        except Exception as e:
            log.error(f"Unexpected error in get_profile: {e}")
            raise

    @staticmethod
    async def get_usernames(db: AsyncSession) -> List[str]:
        """Get profile information of user using user_id, including address and phone numbers as JSON aggregates."""
        try:
            statement = select(User.username).filter(User.username.isnot(None))
            results = await db.execute(statement)
            return results.scalars().all()

        except SQLAlchemyError as db_err:
            log.critical(f"Database error in get_usernames: {db_err}")
            raise

        except Exception as e:
            log.error(f"Unexpected error in get_usernames: {e}")
            raise