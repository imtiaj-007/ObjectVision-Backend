CREATE_USER_RESPONSES = {
    201: {
        "description": "User  created successfully",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "email": "newuser@example.com",
                    "created_at": "2023-10-01T12:00:00Z",
                }
            }
        },
    },
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "example": {"detail": "Email and Password is required for sign-up"}
            }
        },
    },
    403: {
        "description": "Forbidden",
        "content": {
            "application/json": {"example": {"detail": "Only admins can create users"}}
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {"example": {"detail": "An unexpected error occurred"}}
        },
    },
}
