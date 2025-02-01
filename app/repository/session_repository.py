from datetime import datetime, timezone
from typing import Optional
from sqlmodel import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.session_model import UserSession


class SessionRepository:
    @staticmethod
    async def get_session_details(db: AsyncSession, user_id: int) -> Optional[UserSession]:
        """
        Retrieve user session details with comprehensive error handling.        
        Args:
            db: Async database session
            user_id: User identifier
        
        Returns:
            UserSession if found, None otherwise
        
        Raises:
            SQLAlchemyError: If there is an error related to the database during the operation.
            Exception: If an unexpected error occurs during the session expiry update process.
        """
        try:
            query = select(UserSession).where(
                and_(
                    UserSession.user_id == user_id, 
                    UserSession.is_active == True
                )
            ).order_by(UserSession.created_at.desc())
            result = await db.execute(query)
            session_details = result.scalar_one_or_none()
            
            return session_details
        
        except SQLAlchemyError as e:
            print(f"Database error retrieving session details: {e}")
            raise
        except Exception as e:        
            print(f"Unexpected error in get_session_details: {e}")
            raise
    
    @staticmethod
    async def create_new_session(db: AsyncSession, session_data: UserSession) -> UserSession:
        """
        Retrieve user session details with comprehensive error handling.        
        Args:
            db: Async database session
            session_data: UserSession identifier
        
        Returns:
            New UserSession
        
        Raises:
            SQLAlchemyError: If there is an error related to the database during the operation.
            Exception: If an unexpected error occurs during the session expiry update process.
        """
        try:
            new_session = UserSession(**session_data)
            
            db.add(new_session)
            await db.commit()
            await db.refresh(new_session)

            return new_session
        
        except SQLAlchemyError as e:
            print(f"Database error on inserting session details: {e}")
            raise
        except Exception as e:        
            print(f"Unexpected error in create_new_session: {e}")
            raise
    
    @staticmethod
    async def update_access_token(db: AsyncSession, session: UserSession, new_access_token: str) -> int | None:
        """
        Update the access token of an existing session.
        Args:
            db (AsyncSession): The database session.
            session (UserSession): The current session to update.
            new_access_token (str): The new access token to store.
        
        Returns:
            Updated UserSession
        
        Raises:
            SQLAlchemyError: If there is an error related to the database during the operation.
            Exception: If an unexpected error occurs during the session expiry update process.    
        """
        try:
            # Update the access token and update timestamp
            query = (
                update(UserSession)
                .where(UserSession.id == session.id)
                .values(
                    access_token=new_access_token,
                    updated_at=datetime.now(timezone.utc).replace(tzinfo=None)
                )
            )
            result = await db.execute(query)
            await db.commit()            

            return result.rowcount
        
        except SQLAlchemyError as e:
            print(f"Database error on updating token details: {e}")
            raise
        except Exception as e:        
            print(f"Unexpected error in update_access_token: {e}")
            raise
    
    @staticmethod
    async def invalidate_sessions(db: AsyncSession, user_id: int, refresh_token: str, all_devices: bool = False) -> None:
        """
        Invalidate sessions for a user
        Args:
            db: Database session
            user_id: ID of the user
            refresh_token: Current session's refresh token (required if all_devices=False)
            all_devices: If True, invalidate all sessions; if False, invalidate only current session
        """

        conditions = [
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ]
        
        # Add refresh token condition only when logging out from current device
        if not all_devices and refresh_token:
            conditions.append(UserSession.refresh_token == refresh_token)

        query = (
            update(UserSession)
            .where(
                and_(*conditions)
            )
            .values(
                is_active=False,
                updated_at=datetime.now(timezone.utc).replace(tzinfo=None)
            )
        )
        await db.execute(query)
        await db.commit()
    
    @staticmethod
    async def update_expired_sessions(db: AsyncSession) -> None:
        """
        Check and update user sessions that have expired based on their `expires_at` field.
        If the current time exceeds `expires_at`, mark the session as expired.

        Args:
            db (AsyncSession): The asynchronous database session to interact with the database.

        Returns:
            None: This method does not return any value.

        Raises:
            SQLAlchemyError: If there is an error related to the database during the operation.
            Exception: If an unexpected error occurs during the session expiry update process.
        """
        try:
            # Query the sessions that are not expired
            result = await db.execute(select(UserSession).where(UserSession.is_expired == False))
            sessions = result.scalars().all()

            # Loop through and update the expired sessions
            for user_session in sessions:
                if user_session.expires_at and datetime.now(timezone.utc) > user_session.expires_at:
                    user_session.is_expired = True
                    db.add(user_session)

            # Commit the changes to the database
            await db.commit()
        
        except SQLAlchemyError as e:
            print(f"Database error on updating session expiry details: {e}")
            raise
        except Exception as e:        
            print(f"Unexpected error in update_expired_sessions: {e}")
            raise
