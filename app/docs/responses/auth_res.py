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
