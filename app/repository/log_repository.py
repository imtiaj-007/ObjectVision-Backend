from typing import Optional, Dict, Any
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.log_model import Log


class LogRepository:
    """Centralized logging service to store logs in the database."""

    @staticmethod
    async def store_log(
        db: AsyncSession,
        log_data: Dict[str, Any]
    ):
        """Stores a log entry asynchronously in the database."""
        try:
            log_entry = Log(**log_data)

            db.add(log_entry)
            await db.commit()
        
        except Exception as e:
            raise

    @staticmethod
    async def get_logs(session: AsyncSession, log_level: Optional[str] = None):
        """Fetch logs from the database with optional filtering."""
        try:
            conditions = []
            if log_level:
                conditions.append(Log.log_level == log_level)

            query = select(Log).order_by(Log.timestamp.desc())
            result = await session.execute(query)
            return result.scalars().all()

        except Exception as e:
            raise
