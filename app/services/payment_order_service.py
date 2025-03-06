from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.payment_order_repository import PaymentOrderRepository
from app.schemas.payment_schemas import OrderResponse
from app.utils.logger import log


class PaymentOrderService:
    """
    Service class for handling business logic related to Payment orders and payments.
    Uses the PaymentOrderRepository for database operations.
    """

    async def get_all_orders_list(
        db: AsyncSession, page: int, limit: int
    ) -> List[OrderResponse]:
        """Handle offset and other query logics and Get the list of all orders."""
        try:
            offset: int = (page - 1) * limit
            return await PaymentOrderRepository.get_all_orders(db, limit, offset)

        except Exception as e:
            log.error(f"Error in get_all_orders_list service: {str(e)}")
            raise

    
    async def get_all_orders_list_by_user_id(
        db: AsyncSession, user_id: int, page: int, limit: int
    ) -> List[OrderResponse]:
        """Handle offset and other query logics and Get the list of all orders by user_id."""
        try:
            offset: int = (page - 1) * limit
            return await PaymentOrderRepository.get_all_orders_of_user(db, user_id, limit, offset)

        except Exception as e:
            log.error(f"Error in get_all_orders_list_by_user_id service: {str(e)}")
            raise
