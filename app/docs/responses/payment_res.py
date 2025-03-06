ORDER_LIST_RESPONSES = {
    200: {
        "description": "Orders fetched successfully",
        "content": {
            "application/json": {
                "example": {
                    "status": 1,
                    "message": "Orders fetched successfully.",
                    "data": [
                        {
                            "order_id": 12345,
                            "user_id": 101,
                            "status": "pending",
                            "total": 250.00,
                            "created_at": "2025-03-06T10:15:30Z"
                        }
                    ]
                }
            }
        },
    },
    401: {
        "description": "Unauthorized user",
        "content": {
            "application/json": {"example": {"message": "Unauthorized user."}}
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {"example": {"message": "An unexpected error occurred while fetching orders."}}
        },
    },
}

ORDER_LIST_BY_USER_RESPONSES = {
    200: {
        "description": "User orders fetched successfully",
        "content": {
            "application/json": {
                "example": {
                    "status": 1,
                    "message": "User orders fetched successfully.",
                    "data": [
                        {
                            "order_id": 12345,
                            "user_id": 101,
                            "status": "completed",
                            "total": 500.00,
                            "created_at": "2025-03-06T12:45:30Z"
                        }
                    ]
                }
            }
        },
    },
    401: {
        "description": "Unauthorized user",
        "content": {
            "application/json": {"example": {"message": "Unauthorized user."}}
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {"example": {"message": "An unexpected error occurred while fetching user orders."}}
        },
    },
}

ORDER_CREATE_RESPONSES = {
    201: {
        "description": "Order created successfully",
        "content": {
            "application/json": {
                "example": {
                    "status": 1,
                    "message": "Order created successfully.",
                    "data": {
                        "order_id": 12345,
                        "user_id": 101,
                        "status": "pending",
                        "total": 250.00,
                        "created_at": "2025-03-06T10:15:30Z"
                    }
                }
            }
        },
    },
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {"example": {"message": "Invalid order data."}}
        },
    },
    404: {
        "description": "Plan details not found",
        "content": {
            "application/json": {"example": {"message": "Plan details not found."}}
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {"example": {"message": "An unexpected error occurred while creating the order."}}
        },
    },
}

VERIFY_PAYMENT_RESPONSES = {
    200: {
        "description": "Payment verified successfully",
        "content": {
            "application/json": {
                "example": {
                    "status": 1,
                    "message": "Payment verified successfully",
                    "extra_data": {
                        "payment_id": "pay_ABC123",
                        "status": "captured",
                        "amount": 250.00,
                        "currency": "INR"
                    }
                }
            }
        },
    },
    400: {
        "description": "Invalid payment signature",
        "content": {
            "application/json": {"example": {"message": "Invalid payment signature"}}
        },
    },
    404: {
        "description": "Payment details not found",
        "content": {
            "application/json": {"example": {"message": "Payment details not found."}}
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {"example": {"message": "An unexpected error occurred while verifying payment."}}
        },
    },
}

PAYMENT_DETAILS_RESPONSES = {
    200: {
        "description": "Payment details fetched successfully",
        "content": {
            "application/json": {
                "example": {
                    "status": 1,
                    "message": "Payment details fetched successfully.",
                    "data": {
                        "payment_id": "pay_ABC123",
                        "status": "captured",
                        "amount": 250.00,
                        "currency": "INR",
                        "created_at": "2025-03-06T10:45:00Z"
                    }
                }
            }
        },
    },
    401: {
        "description": "Unauthorized user",
        "content": {
            "application/json": {"example": {"message": "Unauthorized user."}}
        },
    },
    404: {
        "description": "Payment details not found",
        "content": {
            "application/json": {"example": {"message": "Payment details not found."}}
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {"example": {"message": "An unexpected error occurred while fetching payment details."}}
        },
    },
}
