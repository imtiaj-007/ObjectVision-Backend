from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, or_, desc
from typing import Optional, Dict, Any, List
from app.db.models.order_model import Order
from app.schemas.payment_schemas import OrderResponse
from app.utils.logger import log


class PaymentOrderRepository:
    """ Datatbase operations related to payments orders and payments """
    @staticmethod
    async def get_all_orders(
        db: AsyncSession,
        limit: int,
        offset: int
    ) -> List[OrderResponse]:
        try:
            statement = (
                select(Order)
                .limit(limit)
                .offset(offset)
                .order_by(desc(Order.created_at))               
            )

            result = await db.execute(statement)
            return result.scalars().all()

        except Exception as e:
            log.critical(f"Database error in get_all_orders: {e}")
            raise

    @staticmethod
    async def get_all_orders_of_user(
        db: AsyncSession,
        user_id: int,
        limit: int,
        offset: int
    ) -> List[OrderResponse]:
        try:
            statement = (
                select(Order)
                .where(Order.user_id == user_id)
                .limit(limit)
                .offset(offset)
                .order_by(desc(Order.created_at))               
            )

            result = await db.execute(statement)
            return result.scalars().all()

        except Exception as e:
            log.critical(f"Database error in get_all_orders_of_user: {e}")
            raise

    @staticmethod
    async def store_order(db: AsyncSession, order_details: Dict[str, Any]) -> OrderResponse:
        try:
            order_data = Order(**order_details)
            db.add(order_data)
            await db.commit()
            await db.refresh(order_data)
            return order_data

        except Exception as e:
            log.critical(f"Database error in store_order: {e}")
            raise

    @staticmethod
    async def update_order(
        db: AsyncSession, order_id: int, update_data: Dict[str, Any]
    ) -> OrderResponse:
        try:
            order = await db.get(Order, order_id)
            if not order:
                raise ValueError(f"Order with ID {order_id} not found")

            # Update fields dynamically
            for key, value in update_data.items():
                if hasattr(order, key):
                    setattr(order, key, value)

            await db.commit()
            await db.refresh(order)
            return order

        except Exception as e:
            log.critical(f"Database error in update_order: {e}")
            raise

    @staticmethod
    async def get_order_details(
        db: AsyncSession,
        order_id: Optional[int] = None,
        razorpay_order_id: Optional[str] = None,
        receipt: Optional[str] = None,
    ) -> Optional[OrderResponse]:
        try:
            filters = []
            if order_id is not None:
                filters.append(Order.id == order_id)
            if razorpay_order_id is not None:
                filters.append(Order.razorpay_order_id == razorpay_order_id)
            if receipt is not None:
                filters.append(Order.receipt == receipt)

            if not filters:
                log.warning("No valid filters provided to get_order_details.")
                return None 

            statement = select(Order).where(or_(*filters))

            result = await db.execute(statement)
            return result.scalar_one_or_none()

        except Exception as e:
            log.critical(f"Database error in get_order_details: {e}")
            raise
