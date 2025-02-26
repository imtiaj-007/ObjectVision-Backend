GET_ALL_ADDRESS_RESPONSES = {
    200: {
        "description": "Addresses retrieved successfully",
        "content": {
            "application/json": {
                "example": [
                    {
                        "id": 1,
                        "user_id": 123,
                        "street": "123 Main St",
                        "city": "New York",
                        "state": "NY",
                        "zip_code": "10001",
                        "country": "USA"
                    }
                ]
            }
        },
    },
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {"example": {"detail": "User authentication required"}}
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {"example": {"detail": "An unexpected error occurred"}}
        },
    },
}

GET_ALL_ADDRESSES_OF_USER_RESPONSES = GET_ALL_ADDRESS_RESPONSES

CREATE_NEW_ADDRESS_RESPONSES = {
    201: {
        "description": "Address created successfully",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "user_id": 123,
                    "street": "123 Main St",
                    "city": "New York",
                    "state": "NY",
                    "zip_code": "10001",
                    "country": "USA"
                }
            }
        },
    },
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {"example": {"detail": "Invalid input data"}}
        },
    },
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {"example": {"detail": "User authentication required"}}
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {"example": {"detail": "An unexpected error occurred"}}
        },
    },
}

UPDATE_ADDRESS_RESPONSES = {
    200: {
        "description": "Address updated successfully",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "user_id": 123,
                    "street": "456 Elm St",
                    "city": "Los Angeles",
                    "state": "CA",
                    "zip_code": "90001",
                    "country": "USA"
                }
            }
        },
    },
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {"example": {"detail": "Invalid input data"}}
        },
    },
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {"example": {"detail": "User authentication required"}}
        },
    },
    404: {
        "description": "Not Found",
        "content": {
            "application/json": {"example": {"detail": "Address not found"}}
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {"example": {"detail": "An unexpected error occurred"}}
        },
    },
}

DELETE_ADDRESS_RESPONSES = {
    200: {
        "description": "Address deleted successfully",
        "content": {
            "application/json": {"example": {"detail": "Address deleted successfully"}}
        },
    },
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {"example": {"detail": "User authentication required"}}
        },
    },
    404: {
        "description": "Not Found",
        "content": {
            "application/json": {"example": {"detail": "Address not found"}}
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {"example": {"detail": "An unexpected error occurred"}}
        },
    },
}
