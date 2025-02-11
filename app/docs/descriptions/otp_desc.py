VERIFY_OTP_DESCRIPTION = (
    description
) = """
Verifies the provided OTP (One-Time Password) for the given user. This endpoint allows users to confirm the validity of the OTP sent to them.

### Parameters:
- **payload (OTPVerify):** The OTP verification data, including the user ID, email, and the OTP.
  - `user_id (int):` The unique identifier for the user.
  - `email (str):` The user's email address.
  - `otp (str):` The OTP sent to the user for verification.

- **db (AsyncSession):** The database session to interact with the OTP repository.

### Returns:
- **GeneralResponse:** Contains the status and a message indicating whether the OTP verification was successful.

### Raises:
- `HTTPException(400):` If the OTP or required fields (user ID or email) are missing.
- `HTTPException(404):` If the OTP is expired or invalid.
- `HTTPException(500):` For unexpected server errors.

### Flow:
1. Checks if the OTP and necessary fields (user ID or email) are provided.
2. Retrieves the stored OTP from the database and compares it with the provided OTP.
3. If the OTP is valid, marks it as used and updates the user's status in the database.
4. Returns a success message if the OTP is verified.

### Example Success Response:
```json
{
    "status": 1,
    "message": "OTP verified successfully."
}
```

### Example Error Responses:
- `400 Bad Request:` Missing OTP or Required Fields:
```json
{
    "detail": "OTP is missing, Please check and retry."
}
```
- `404 Not Found:` Invalid or Expired OTP:
```json
{
    "detail": "OTP is expired or Invalid"
}
```

### This endpoint:
1. Validates the OTP for the given user.
2. Marks the OTP as used once verified.
3. Updates the user's status upon successful OTP verification.

Ensure that the OTP is valid and that the required user details are provided to avoid errors during verification.
"""

RESEND_OTP_DESCRIPTION = (
    description
) = """
Resends a new OTP (One-Time Password) to the user after validating their previous OTP status. This endpoint ensures that OTPs are not requested too frequently by the user and manages the expiration and reuse of OTPs.

### Parameters:
- **payload (OTPResend):** The data required to resend the OTP.
  - `user_id (int):` The unique identifier of the user.
  - `email (str):` The user's email address.
  - `type (str):` The type of OTP to send, such as `"email_verification"`.
  - `expiry_minutes (int):` The expiration time for the OTP in minutes. Default 10 minutes.

- **db (AsyncSession):** The database session to interact with the OTP service.

### Returns:
- **GeneralResponse:** Contains the status and a message indicating whether the OTP resend operation was successful.

### Raises:
- `HTTPException(400):` If neither `user_id` nor `email` is provided in the request payload.
- `HTTPException(404):` If the user is not found in the system.
- `HTTPException(429):` If the user requests an OTP before 1 minute has passed.
- `HTTPException(500):` For unexpected server errors.

### Flow:
1. Verifies if either `user_id` or `email` is provided in the request.
2. Checks if there is an active OTP for the user and if enough time has passed since the last OTP request.
3. If the last OTP request was too recent (less than 1 minute ago), a `429 Too Many Requests` error is raised.
4. If there is an active OTP, it is invalidated, and a new OTP is generated and sent.
5. Returns a success message if the new OTP is resent successfully.

### Example Success Response:
```json
{
    "status": 1,
    "message": "New OTP has been sent successfully."
}
```

### Example Error Responses:
- `400 Bad Request:` Missing User ID or Email:
```json
{
    "detail": "Either user_id or email is required"
}
```
- `429 Too Many Requests:` User tries to send multiple requests.
```json
{
    "detail": "Please wait for 1 minute before requesting a new OTP"
}
```
- `500 Internal Server Error:`
```json
{
    "detail": "An unexpected error occurred"
}
```

### This endpoint:
1. Verifies that enough time has passed before a new OTP can be requested.
2. Resends a new OTP to the user after invalidating the previous one.
3. Ensures that the OTP request process is rate-limited to avoid abuse.

Ensure that the user has either provided a valid `user_id` or `email`, and that enough time has passed since their last OTP request to avoid errors. 
"""