VERIFY_OTP_RESPONSES = {
    200: {
        "description": "OTP verified successfully",
        "content": {
            "application/json": {
                "example": {"status": 1, "message": "OTP verified successfully."}
            }
        },
    },
    400: {
        "description": "Bad Request - Missing OTP or Required Fields",
        "content": {
            "application/json": {
                "example": {"detail": "OTP is missing, Please check and retry."}
            }
        },
    },
    404: {
        "description": "Not Found - Invalid or Expired OTP",
        "content": {
            "application/json": {"example": {"detail": "OTP is expired or Invalid"}}
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {"example": {"detail": "An unexpected error occurred"}}
        },
    },
}

RESEND_OTP_RESPONSES = {
    200: {
        "description": "New OTP has been sent successfully",
        "content": {
            "application/json": {
                "example": {
                    "status": 1,
                    "message": "New OTP has been sent successfully.",
                }
            }
        },
    },
    400: {
        "description": "Bad Request - Either user_id or email is required",
        "content": {
            "application/json": {
                "example": {"detail": "Either user_id or email is required"}
            }
        },
    },
    429: {
        "description": "Too Many Requests - Please wait for 1 minute before requesting a new OTP",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Please wait for 1 minute before requesting a new OTP"
                }
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
