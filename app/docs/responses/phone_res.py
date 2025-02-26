GET_ALL_PHONES_RESPONSES = {
    200: {
        "description": "Phone numbers retrieved successfully",
        "content": {
            "application/json": {
                "example": [
                    {
                        "id": 1,
                        "user_id": 123,
                        "phone_number": "+1234567890",
                        "is_primary": True,
                        "label": "Home"
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

GET_ALL_PHONES_OF_USER_RESPONSES = GET_ALL_PHONES_RESPONSES

CREATE_NEW_PHONE_RESPONSES = {
    201: {
        "description": "Phone number created successfully",
        "content": {
            "application/json": {
                "example": {"message": "New phone number created successfully."}
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

UPDATE_PHONE_RESPONSES = {
    200: {
        "description": "Phone number updated successfully",
        "content": {
            "application/json": {
                "example": {"message": "Phone number updated successfully."}
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
            "application/json": {"example": {"detail": "Phone number not found"}}
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {"example": {"detail": "An unexpected error occurred"}}
        },
    },
}

DELETE_PHONE_RESPONSES = {
    200: {
        "description": "Phone number deleted successfully",
        "content": {
            "application/json": {"example": {"message": "Phone number deleted successfully."}}
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
            "application/json": {"example": {"detail": "Phone number not found"}}
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {"example": {"detail": "An unexpected error occurred"}}
        },
    },
}
