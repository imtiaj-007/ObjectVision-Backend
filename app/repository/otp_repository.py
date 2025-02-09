from typing import Dict, Any
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.db.models.otp_model import OTP
from app.utils.logger import log


class OTPRepository:
    @staticmethod
    async def store_otp(db: AsyncSession, otp_data: Dict[str, Any]) -> OTP:
        """Create a new OTP record"""
        try:
            db_otp = OTP(**otp_data)
            db.add(db_otp)

            await db.commit()
            await db.refresh(db_otp)
            return db_otp

        except SQLAlchemyError as db_error:
            log.critical(f"Database error in store_otp: {db_error}")
            raise

        except Exception as e:
            log.critical(f"An Unexpected error at store_otp: {e}")
            raise

    @staticmethod
    async def get_latest_active_otp(db: AsyncSession, user_id: int) -> Optional[OTP]:
        """
        Get the most recent active (not expired, not used) OTP for a user
        """
        try:
            current_time = datetime.now(timezone.utc).replace(tzinfo=None)
            query = (
                select(OTP)
                .where(
                    OTP.user_id == user_id,
                    OTP.is_used == False,
                    OTP.expires_at > current_time,
                )
                .order_by(OTP.created_at.desc())
            )

            result = await db.execute(query)
            return result.scalar_one_or_none()
        
        except SQLAlchemyError as db_error:
            log.critical(f"Database error in get_latest_active_otp: {db_error}")
            raise

        except Exception as e:
            log.critical(f"An Unexpected error at get_latest_active_otp: {e}")
            raise

    @staticmethod
    async def get_valid_otp(db: AsyncSession, user_id: str, otp: str) -> Optional[OTP]:
        """Get valid (not expired, not used) OTP"""
        statement = select(OTP).where(
            OTP.user_id == user_id,
            OTP.otp == otp,
            OTP.is_used == False,
            OTP.expires_at > datetime.now(timezone.utc).replace(tzinfo=None),
        )

        try:
            result = await db.execute(statement)
            return result.scalar_one_or_none()

        except SQLAlchemyError as db_error:
            log.critical(f"Database error in get_valid_otp: {db_error}")
            raise

        except Exception as e:
            log.critical(f"An Unexpected error at get_valid_otp: {e}")
            raise

    @staticmethod
    async def mark_otp_used(db: AsyncSession, otp_record: OTP) -> OTP:
        """Mark OTP as used"""
        try:
            otp_record.is_used = True
            otp_record.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
            await db.commit()
            await db.refresh(otp_record)
            return otp_record

        except SQLAlchemyError as db_error:
            log.critical(f"Database error in mark_otp_used: {db_error}")
            raise

        except Exception as e:
            log.critical(f"An Unexpected error at mark_otp_used: {e}")
            raise

    @staticmethod
    async def increment_attempt_count(db: AsyncSession, otp_record: OTP) -> OTP:
        """Increment the attempt count for an OTP"""
        try:
            otp_record.attempt_count += 1
            otp_record.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
            await db.commit()
            await db.refresh(otp_record)
            return otp_record

        except SQLAlchemyError as db_error:
            log.critical(f"Database error in increment_attempt_count: {db_error}")
            raise

        except Exception as e:
            log.critical(f"An Unexpected error at increment_attempt_count: {e}")
            raise

    @staticmethod
    async def cleanup_expired_otps(db: AsyncSession) -> int:
        """Delete expired OTPs"""
        statement = select(OTP).where(
            OTP.expires_at < datetime.now(timezone.utc).replace(tzinfo=None),
            OTP.is_used == False,
        )
        try:
            result = await db.exec(statement)
            expired_otps = result.scalars().all()

            for otp in expired_otps:
                await db.delete(otp)

            await db.commit()
            return len(expired_otps)

        except SQLAlchemyError as db_error:
            log.critical(f"Database error in cleanup_expired_otps: {db_error}")
            raise

        except Exception as e:
            log.critical(f"An Unexpected error at cleanup_expired_otps: {e}")
            raise
