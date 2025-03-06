import json
import hmac
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

import razorpay
from fastapi import HTTPException, Request
import razorpay.errors
from app.configuration.config import settings
from app.schemas.payment_schemas import (
    PaymentOrderRequest,
    RefundRequest,
    CustomerRequest,
)
from app.schemas.user_schema import UserData
from app.schemas.subscription_schema import SubscriptionPlanResponse
from app.tasks.taskfiles.subscription_task import store_order_task
from app.utils.logger import log


class RazorpayService:
    """
    A comprehensive service for handling Razorpay payment operations in a FastAPI application.

    This service provides methods for:
    - Creating orders
    - Verifying payments
    - Handling refunds
    - Managing customers
    - Processing webhooks
    - Fetching payment details and history
    """

    def __init__(
        self,
        key_id: str = None,
        key_secret: str = None,
        webhook_secret: str = None,
    ):
        """Initialize the Razorpay service with configuration"""

        self.key_id = key_id or settings.RAZORPAY_KEY_ID
        self.key_secret = key_secret or settings.RAZORPAY_KEY_SECRET
        self.webhook_secret = webhook_secret or settings.RAZORPAY_WEBHOOK_SECRET

        # Initialize Razorpay client
        self.client = razorpay.Client(auth=(self.key_id, self.key_secret))

    async def create_order(
        self,
        user: UserData,
        order_data: PaymentOrderRequest,
        plan_details: SubscriptionPlanResponse,
    ) -> Dict[str, Any]:
        """
        Create a new payment order

        Args:
            order_data: Order details containing amount, currency, etc.

        Returns:
            Razorpay order object
        """
        try:
            # Convert amount to paise (smallest currency unit)
            amount_in_paise = int(plan_details.amount * 100)

            # Prepare order data
            order_dict = {
                "amount": amount_in_paise,
                "currency": order_data.currency,
                "receipt": order_data.receipt or f"receipt_{datetime.now()}",
                "notes": order_data.notes or {},
            }

            if order_data.description:
                order_dict["notes"]["description"] = order_data.description

            # Create order
            response = self.client.order.create(data=order_dict)  
            razorpay_id = response["id"]
            del response["id"]          

            # Enhance response with additional information
            enhanced_response = {
                **response,
                "razorpay_order_id": razorpay_id,
                "plan_id": plan_details.id,
                "plan_name": plan_details.name,
                "description": plan_details.description,
                "promo_code": order_data.promo_code or None,
            }

            store_order_task.delay(user.id, {
                **enhanced_response, 
                "amount": plan_details.amount
            })
            return enhanced_response

        except razorpay.errors.BadRequestError as e:
            log.critical(f"Order creation failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))

        except Exception as e:
            log.error(f"Unexpected Error: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to create payment order"
            )

    async def verify_payment(
        self, payment_id: str, order_id: str, signature: str
    ) -> bool:
        """
        Verify payment signature

        Args:
            payment_id: Razorpay payment ID
            order_id: Razorpay order ID
            signature: Razorpay signature

        Returns:
            True if verification succeeds
        """
        try:
            # Create signature verification data
            verification_data = f"{order_id}|{payment_id}"

            # Generate expected signature
            expected_signature = hmac.new(
                self.webhook_secret.encode(), verification_data.encode(), hashlib.sha256
            ).hexdigest()

            # Verify signature
            is_valid = hmac.compare_digest(expected_signature, signature)

            if is_valid:
                log.success(f"Payment: {payment_id} verified successfully")                            
            else:
                log.critical(f"Payment: {payment_id} not verified")                

            return is_valid

        except Exception as e:
            log.critical(f"Payment verification error: {e}")
            raise HTTPException(status_code=500, detail="Payment verification failed")

    async def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """
        Fetch payment details by ID

        Args:
            payment_id: Razorpay payment ID

        Returns:
            Payment details
        """
        try:
            payment = self.client.payment.fetch(payment_id)
            log.success(f"payment_id: {payment_id}, Fetched payment details")
            return payment

        except Exception as e:
            log.critical(f"payment_id: {payment_id}, Error fetching payment, error: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to fetch payment details"
            )

    async def create_refund(self, refund_data: RefundRequest) -> Dict[str, Any]:
        """
        Create a refund for a payment

        Args:
            refund_data: Refund details

        Returns:
            Refund details
        """
        try:
            refund_dict = {"notes": refund_data.notes or {}, "speed": refund_data.speed}

            # If amount is specified, convert to paise
            if refund_data.amount:
                refund_dict["amount"] = int(refund_data.amount * 100)

            refund = self.client.payment.refund(refund_data.payment_id, refund_dict)

            log.success(
                f"Refund created",
                {"payment_id": refund_data.payment_id, "refund_id": refund.get("id")},
            )
            return refund

        except razorpay.errors.BadRequestError as e:
            log.critical(f"Refund creation failed: Bad request", e.error, "error")
            raise HTTPException(status_code=400, detail=str(e))

        except Exception as e:
            log.critical(f"Refund creation failed", str(e), "error")
            raise HTTPException(status_code=500, detail="Failed to process refund")

    async def create_customer(self, customer_data: CustomerRequest) -> Dict[str, Any]:
        """
        Create a new customer

        Args:
            customer_data: Customer details

        Returns:
            Customer details
        """
        try:
            customer = self.client.customer.create(
                {
                    "name": customer_data.name,
                    "email": customer_data.email,
                    "contact": customer_data.contact,
                    "notes": customer_data.notes or {},
                }
            )

            log.info("Customer created", {"customer_id": customer.get("id")})
            return customer

        except razorpay.errors.BadRequestError as e:
            log.critical(f"Customer creation failed: Bad request", e.error, "error")
            raise HTTPException(status_code=400, detail=str(e))

        except Exception as e:
            log.critical(f"Customer creation failed", str(e), "error")
            raise HTTPException(status_code=500, detail="Failed to create customer")

    async def process_webhook(self, request: Request) -> Dict[str, Any]:
        """
        Process Razorpay webhook

        Args:
            request: FastAPI request object

        Returns:
            Processed webhook data
        """
        try:
            # Get request body and headers
            body = await request.body()
            body_str = body.decode()

            # Get signature from headers
            signature = request.headers.get("X-Razorpay-Signature")

            if not signature:
                raise HTTPException(status_code=400, detail="Missing webhook signature")

            # Verify signature
            is_valid = self._verify_webhook_signature(body_str, signature)

            if not is_valid:
                log.critical("Invalid webhook signature", {}, "error")
                raise HTTPException(status_code=400, detail="Invalid webhook signature")

            # Parse payload
            payload = json.loads(body_str)
            event = payload.get("event")

            log.success(
                f"Webhook received: {event}",
                {
                    "event": event,
                    "entity_id": payload.get("payload", {})
                    .get("payment", {})
                    .get("entity", {})
                    .get("id"),
                },
            )

            return payload

        except json.JSONDecodeError:
            log.error("Invalid webhook JSON", {}, "error")
            raise HTTPException(status_code=400, detail="Invalid webhook payload")

        except Exception as e:
            log.error(f"Webhook processing error", str(e), "error")
            raise HTTPException(status_code=500, detail="Failed to process webhook")

    def _verify_webhook_signature(self, body: str, signature: str) -> bool:
        """Verify webhook signature"""
        generated_signature = hmac.new(
            self.webhook_secret.encode(), body.encode(), hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(generated_signature, signature)

    async def get_payment_history(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        count: int = 10,
        skip: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get payment history for a date range

        Args:
            from_date: Start date
            to_date: End date
            count: Number of records to fetch
            skip: Number of records to skip

        Returns:
            List of payment records
        """
        try:
            # Prepare filter parameters
            params = {"count": min(count, 100), "skip": skip}  # Limit to max 100

            if from_date:
                params["from"] = int(from_date.timestamp())

            if to_date:
                params["to"] = int(to_date.timestamp())

            # Fetch payments
            payments = self.client.payment.all(params)

            log.info(
                f"Fetched payment history",
                {
                    "count": len(payments.get("items", [])),
                    "from_date": from_date,
                    "to_date": to_date,
                },
            )

            return payments.get("items", [])

        except Exception as e:
            log.error(f"Error fetching payment history", str(e), "error")
            raise HTTPException(
                status_code=500, detail="Failed to fetch payment history"
            )


# Dependency to inject the service into routes
def get_razorpay_service() -> RazorpayService:
    return RazorpayService()
