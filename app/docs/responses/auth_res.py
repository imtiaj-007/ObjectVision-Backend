LOGIN_RESPONSES = {
    200: {
        "description": "Successfully authenticated user",
        "content": {
            "application/json": {
                "example": {
                    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                }
            }
        },
    },
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {"example": {"detail": "Invalid username or password"}}
        },
    },
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {"example": {"detail": "User  is not authorized"}}
        },
    },
    409: {
        "description": "Conflict - User logged in with another device",
        "content": {
            "application/json": {
                "example": {"detail": "You are already logged in from another device."}
            }
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {"example": {"detail": "An unexpected error occurred"}}
        },
    },
}

SIGNUP_RESPONSES = {
    201: {
        "description": "User created successfully",
        "content": {
            "application/json": {
                "example": {
                    "status": 1,
                    "message": "User registration successful",
                    "user_id": 1,
                    "email": "user@example.com",
                }
            }
        },
    },
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "example": {"detail": "Email and Password are required for sign-up"}
            }
        },
    },
    409: {
        "description": "Conflict - Email already exists",
        "content": {
            "application/json": {
                "example": {"detail": "The email address is already registered"}
            }
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {"example": {"detail": "An unexpected error occurred"}}
        },
    },
}

GOOGLE_OAUTH_RESPONSES = {
    302: {
        "description": "Redirect to Google OAuth",
        "headers": {
            "Location": {
                "description": "URL to redirect to Google OAuth login",
                "schema": {"type": "string"},
            }
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {"example": {"detail": "An unexpected error occurred"}}
        },
    },
}

GOOGLE_OAUTH_CALLBACK_RESPONSES = {
    200: {
        "description": "Successfully authenticated with Google",
        "content": {
            "application/json": {
                "example": {
                    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "token_type": "Bearer",
                }
            }
        },
    },
    302: {
        "description": "Redirect to frontend with token or error",
        "headers": {
            "Location": {
                "description": "URL to redirect to",
                "schema": {"type": "string"},
            }
        },
    },
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "example": {"detail": "State mismatch. Possible CSRF attack."}
            }
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {"example": {"detail": "An unexpected error occurred"}}
        },
    },
}

REGENERATE_TOKEN_RESPONSES = {
    200: {
        "description": "New token generated Successfully",
        "content": {
            "application/json": {
                "example": {
                    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                }
            }
        },
    },
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {"example": {"detail": "refresh_token is Invalid."}}
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {"example": {"detail": "An unexpected error occurred"}}
        },
    },
}

LOGOUT_RESPONSES = {
    200: {
        "description": "Successfully logged out",
        "content": {
            "application/json": {
                "example": {"message": "You have successfully logged out."}
            }
        },
    },
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {"example": {"detail": "User  is not authorized"}}
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {"example": {"detail": "An unexpected error occurred"}}
        },
    },
}
