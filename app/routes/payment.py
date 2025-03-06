from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.configuration.config import settings
from app.db.database import db_session_manager
from app.services.auth_service import AuthService
from app.services.subscription_service import SubscriptionService
from app.services.payment_order_service import PaymentOrderService
from app.services.razorpay_service import RazorpayService, get_razorpay_service
from app.schemas.payment_schemas import (
    PaymentVerificationRequest, OrderResponse,
    PaymentOrderRequest, PaymentOrderResponse,
    RazorpayPaymentDetails
)
from app.schemas.general_schema import SuccessResponse

from app.docs.descriptions import payment_desc
from app.docs.responses import payment_res
from app.tasks.taskfiles.subscription_task import update_order_task
from app.utils import helpers
from app.utils.logger import log


router = APIRouter()


@router.get(
    "/orders", 
    response_model=List[OrderResponse], 
    status_code=status.HTTP_200_OK,
    responses=payment_res.ORDER_LIST_RESPONSES,
    summary="Get All Orders",
    description=payment_desc.GET_ALL_ORDERS_DESCRIPTION
)
async def get_all_orders(
    page: int = Query(settings.DEFAULT_PAGE),
    limit: int = Query(settings.DEFAULT_PAGE_LIMIT),
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
    db: AsyncSession = Depends(db_session_manager.get_db),
):
    """ Get the list of all orders """
    try:
        if not auth_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user."
            )
        return await PaymentOrderService.get_all_orders_list(db, page, limit)

    except Exception as e:
        log.error(f"Unexpected error in get_all_orders: {str(e)}")
        raise


@router.get(
    "/orders/{user_id}",
    response_model=List[OrderResponse],
    status_code=status.HTTP_200_OK,
    responses=payment_res.ORDER_LIST_BY_USER_RESPONSES,
    summary="Get All Orders of a User",
    description=payment_desc.GET_ALL_ORDERS_BY_USER_DESCRIPTION
)
async def get_all_orders_by_user(
    user_id: int,
    page: int = Query(settings.DEFAULT_PAGE),
    limit: int = Query(settings.DEFAULT_PAGE_LIMIT),
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
    db: AsyncSession = Depends(db_session_manager.get_db),
):
    """ Get the list of all orders by user_id """
    try:
        if not auth_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user."
            )
        return await PaymentOrderService.get_all_orders_list_by_user_id(db, user_id, page, limit)

    except Exception as e:
        log.error(f"Unexpected error in get_all_orders_by_user: {str(e)}")
        raise


@router.post(
    "/create-order",
    response_model=PaymentOrderResponse,
    status_code=status.HTTP_201_CREATED,
    responses=payment_res.ORDER_CREATE_RESPONSES,
    summary="Create new Payment Order",
    description=payment_desc.CREATE_ORDER_DESCRIPTION
)
async def create_order(
    order_data: PaymentOrderRequest,
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
    razorpay_service: RazorpayService = Depends(get_razorpay_service),
    db: AsyncSession = Depends(db_session_manager.get_db),
):
    """ Create a new payment order with Razorpay """
    try:
        plan_details = await SubscriptionService.get_subscription_plan(db, order_data.plan_id)

        if not plan_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Plan details not found."
            )
        return await razorpay_service.create_order(
            auth_obj["user"], order_data, plan_details
        )

    except Exception as e:
        log.error(f"Unexpected error in create_order: {str(e)}")
        raise


@router.post(
    "/verify", 
    response_model=SuccessResponse, 
    status_code=status.HTTP_200_OK,
    responses=payment_res.VERIFY_PAYMENT_RESPONSES,
    summary="Verify a Payment",
    description=payment_desc.VERIFY_PAYMENT_DESCRIPTION
)
async def verify_payment(
    verification_data: PaymentVerificationRequest,
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
    razorpay_service: RazorpayService = Depends(get_razorpay_service),
):
    """ Verify a payment after it's completed """
    try:
        is_valid = await razorpay_service.verify_payment(
            verification_data.razorpay_payment_id,
            verification_data.razorpay_order_id,
            verification_data.razorpay_signature,
        )

        payment_details = await razorpay_service.get_payment_details(
            verification_data.razorpay_payment_id
        )
        if not is_valid and not payment_details["captured"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment signature"
            )

        user_data = helpers.serialize_datetime_object(auth_obj["user"].model_dump())
        update_order_task.delay(
            razorpay_order_id=payment_details.get('order_id'),
            payment_status=payment_details["status"],
            user=user_data, 
        )

        return {
            "status": 1,
            "message": "Payment verified successfully",
            "extra_data": payment_details,
        }

    except Exception as e:
        log.error(f"Unexpected error in verify_payment: {str(e)}")
        raise


@router.get(
    "/details/{payment_id}",
    response_model=RazorpayPaymentDetails,
    status_code=status.HTTP_200_OK,
    responses=payment_res.PAYMENT_DETAILS_RESPONSES,
    summary="Get Payment Details",
    description=payment_desc.GET_PAYMENT_DETAILS_DESCRIPTION
)
async def get_payment_details(
    payment_id: str, 
    auth_obj: Optional[Dict[str, Any]] = Depends(AuthService.authenticate_user),
    razorpay_service: RazorpayService = Depends(get_razorpay_service)
):
    """ Get details of a specific payment by payment_id """
    try:
        if not auth_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user."
            )
        return await razorpay_service.get_payment_details(payment_id)
    
    except Exception as e:
        log.error(f"Unexpected error in get_payment_details: {e}")
        raise
