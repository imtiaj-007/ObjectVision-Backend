from typing import Any, Dict
from datetime import datetime, timedelta, timezone
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status

from app.repository.user_repository import UserRepository
from app.repository.otp_repository import OTPRepository
from app.schemas.user_schema import UserData
from app.schemas.otp_schema import OTPVerify

from app.utils import helpers
from app.tasks.taskfiles.email_task import send_otp_email_task, send_welcome_email_task


class OTPService:
    @staticmethod
    async def create_otp(
        db: AsyncSession,
        user: UserData,
        type: str = "email_verification",
        expiry_minutes: int = 10,
    ):
        otp = helpers.generate_otp()

        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=expiry_minutes
        )
        otp_data: Dict[str, Any] = {
            "user_id": user.id,
            "email": user.email,
            "otp": otp,
            "type": type,
            "expires_at": expires_at,
        }

        await OTPRepository.store_otp(db, otp_data)

        recipient = {"email": user.email, "name": user.name}
        send_otp_email_task.delay(recipient, otp)

    @staticmethod
    async def check_otp(db: AsyncSession, payload: OTPVerify):
        user_id, email, otp = payload.user_id, payload.email, payload.otp
        if not otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP is missing, Please check and retry.",
            )

        if not user_id and not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User id and email fields are missing",
            )

        stored_otp = await OTPRepository.get_valid_otp(db, user_id, otp)

        if not stored_otp or stored_otp.otp != otp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OTP is expired or Invalid",
            )

        await OTPRepository.mark_otp_used(db, stored_otp)

        payload = {
            "is_active": True,
            "updated_at": datetime.now(timezone.utc),
            "updated_by": user_id,
        }
        await UserRepository.update_user(db, user_id, payload)

        recipient = {"email": email, "name": ""}
        send_welcome_email_task.delay(recipient)

        return {"status": 1, "message": "OTP verified successfully."}

    @classmethod
    async def resend_otp(
        cls,
        db: AsyncSession,
        user_id: int = None,
        email: str = None,
        type: str = "email_verification",
        expiry_minutes: int = 10,
    ):
        """
        Resend OTP to user after validating their previous OTP status
        """        
        active_otp = await OTPRepository.get_latest_active_otp(db, user_id)

        # If there's an active OTP, check if enough time has passed since last request
        if active_otp:
            time_since_last_otp = (
                datetime.now(timezone.utc) - active_otp.created_at
            )
            if time_since_last_otp < timedelta(minutes=1):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Please wait for 1 minute before requesting a new OTP",
                )

            # Invalidate previous OTP
            await OTPRepository.mark_otp_used(db, active_otp)

        # Create new OTP
        user_response = UserData(id=user_id, email=email)
        await cls.create_otp(db, user_response, type, expiry_minutes)

        return {"status": 1, "message": "New OTP has been sent successfully"}
