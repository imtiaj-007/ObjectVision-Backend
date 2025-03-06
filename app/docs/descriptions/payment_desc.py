GET_ALL_ORDERS_DESCRIPTION = """
Retrieves a list of all orders, used by admins, sub-admins and stake holders.

### Parameters:
- **page (int):** The page number for pagination.
- **limit (int):** The number of orders per page.
- **auth_obj (Optional[Dict[str, Any]]):** Authentication details of the user.
- **db (AsyncSession):** Database session for fetching orders.

### Returns:
- **List[OrderResponse]:** A list of orders.

### Raises:
- `HTTPException(401)`: If the user is unauthorized.
- `HTTPException(500)`: For unexpected server errors.

### Flow:
1. Validates authentication.
2. Fetches paginated orders from the database.
3. Returns the order list.

### Example Success Response:
```json
[
    {"order_id": 123, "status": "pending", "total": 250.00},
    {"order_id": 124, "status": "completed", "total": 150.00}
]
```

### Example Error Response:
```json
{
    "detail": "Unauthorized access"
}
```

### This endpoint:
1. Fetches all orders
2. Ensures only the admin, sub-admin, stake holders can access all order history
3. Returns a list of order summaries
"""

GET_ALL_ORDERS_BY_USER_DESCRIPTION = """
Retrieves a paginated list of orders for a specific user.

### Parameters:
- **user_id (int):** The unique identifier of the user.
- **page (int):** The page number for pagination.
- **limit (int):** The number of orders per page.
- **auth_obj (Optional[Dict[str, Any]]):** Authentication details.
- **db (AsyncSession):** Database session for fetching orders.

### Returns:
- **List[OrderResponse]:** A list of the user's orders.

### Raises:
- `HTTPException(401)`: If the user is unauthorized.
- `HTTPException(500)`: For unexpected server errors.

### Flow:
1. Validates authentication.
2. Fetches the user's orders from the database.
3. Returns the order list.

### Example Success Response:
```json
[
    {"order_id": 456, "status": "created", "total": 300.00},
    {"order_id": 489, "status": "captured", "total": 100.00}
]
```

### Example Error Response:
```json
{
    "detail": "Unauthorized access"
}
```

### This endpoint:
1. Fetches all orders for the logged-in user
2. Ensures only the user can access their order history
3. Returns a list of order summaries
"""

CREATE_ORDER_DESCRIPTION = """
Creates a new order in the system. This endpoint allows users to place an payment order by providing order details.

### Parameters:
- **order_data (PaymentOrderRequest):** The order details including plan ID.
- **auth_obj (Optional[Dict[str, Any]]):** Authentication details.
- **razorpay_service (RazorpayService):** Razorpay integration service.
- **db (AsyncSession):** Database session for processing orders.

### Returns:
- **PaymentOrderResponse:** Contains the created order details.

### Raises:
- `HTTPException(404)`: If the plan details are not found.
- `HTTPException(500)`: For unexpected server errors.

### Flow:
1. Validates authentication.
2. Retrieves the subscription plan.
3. Creates an order in Razorpay.
4. Returns the created order details.

### Example Success Response:
```json
{
    "order_id": "order_xyz",
    "amount": 500,
    "currency": "INR",
    "status": "created"
}
```

### Example Error Response:
```json
{
    "detail": "Plan not found"
}
```

### This endpoint:
1. Accepts order details from the user
2. Validates and processes the order
3. Returns the created order details
"""

VERIFY_PAYMENT_DESCRIPTION = """
Verifies a payment after completion.

### Parameters:
- **verification_data (PaymentVerificationRequest):** Payment verification details.
- **auth_obj (Optional[Dict[str, Any]]):** Authentication details.
- **razorpay_service (RazorpayService):** Razorpay integration service.

### Returns:
- **SuccessResponse:** Payment verification result.

### Raises:
- `HTTPException(400)`: If the payment verification fails.
- `HTTPException(500)`: For unexpected server errors.

### Flow:
1. Verifies the payment using Razorpay.
2. Checks if the payment was captured.
3. Updates the order status.
4. Returns the verification status.

### Example Success Response:
```json
{
    "status": 1,
    "message": "Payment verified successfully",
    "extra_data": {"payment_status": "captured"}
}
```

### Example Error Response:
```json
{
    "detail": "Invalid Payment Signatures"
}
```

### This endpoint:
1. Accepts razorpay payment details from the user
2. Validates and verifies the payment status
3. Returns the created payment details
```"""

GET_PAYMENT_DETAILS_DESCRIPTION = """
Retrieves details of a specific payment by payment ID.

### Parameters:
- **payment_id (str):** The unique identifier of the payment.
- **auth_obj (Optional[Dict[str, Any]]):** Authentication details.
- **razorpay_service (RazorpayService):** Razorpay integration service.

### Returns:
- **RazorpayPaymentDetails:** The payment details.

### Raises:
- `HTTPException(401)`: If the user is unauthorized.
- `HTTPException(404)`: If payment details not found for the payment_id.
- `HTTPException(500)`: For unexpected server errors.

### Flow:
1. Validates authentication.
2. Fetches payment details from Razorpay.
3. Returns the payment information.

### Example Success Response:
```json
{
    "payment_id": "pay_xyz",
    "amount": 500,
    "currency": "INR",
    "status": "captured"
}
```

### Example Error Response:
```json
{
    "detail": "Payment details not found."
}
```

### This endpoint:
1. Validates authentication.
2. Fetches payment details from Razorpay.
3. Returns the payment information.
"""
