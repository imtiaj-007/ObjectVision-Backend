from datetime import datetime, timezone
from sqlmodel import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.db.schemas.session_schema import UserSession


class SessionRepository:
    @staticmethod
    async def get_session_details(db: AsyncSession, user_id: int) -> UserSession | None:
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
                    UserSession.is_expired == False
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
            new_session = UserSession(session_data)
            
            # Add to the session and commit
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
    async def update_expired_sessions(db: AsyncSession):
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
