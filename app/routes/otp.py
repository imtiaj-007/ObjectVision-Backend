from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import db_session_manager
from app.services.otp_service import OTPService
from app.schemas.otp_schema import OTPVerify, OTPResend
from app.schemas.auth_schema import GeneralResponse

from app.docs.descriptions import otp_desc
from app.docs.responses import otp_res


router = APIRouter()


@router.get(
    "/", 
    status_code=status.HTTP_200_OK
)
async def send_otp(
    db: AsyncSession = Depends(db_session_manager.get_db),
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Currently this route has no usecase."
    )


@router.post(
    "/verify", 
    response_model=GeneralResponse,
    responses=otp_res.VERIFY_OTP_RESPONSES,
    status_code=status.HTTP_200_OK,
    description=otp_desc.VERIFY_OTP_DESCRIPTION
)
async def verify_otp(
    payload: OTPVerify,
    db: AsyncSession = Depends(db_session_manager.get_db),
):
    """OTP route to verify OTP"""
    return await OTPService.check_otp(db, payload)


@router.post(
    "/resend", 
    response_model=GeneralResponse, 
    responses=otp_res.RESEND_OTP_RESPONSES,
    status_code=status.HTTP_200_OK,
    description=otp_desc.RESEND_OTP_DESCRIPTION
)
async def resend_otp(
    payload: OTPResend,
    db: AsyncSession = Depends(db_session_manager.get_db),
):
    if not payload.user_id and not payload.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either user_id or email is required",
        )
    return await OTPService.resend_otp(db, payload.user_id, payload.email)
