GET_ALL_PHONES_DESCRIPTION = """
Retrieves all phone numbers stored in the system.

### Parameters
- `page (int)`: The page number for pagination.
- `limit (int, optional, default=10)`: The number of phone numbers per page.
- `db (AsyncSession)`: Database session for fetching phone numbers.
- `auth_obj (Optional[Dict[str, Any]])`: The authenticated user object.

### Returns
- `List[PhoneNumberResponse]`: A list of phone number records.

### Raises
- `HTTPException(401)`: If the user is not authenticated.
- `HTTPException(403)`: If the user does not have permission.

### Flow
1. Checks authentication status.
2. Fetches paginated phone numbers from the database.
3. Returns the phone number list.

### Example Success Response
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "user_id": 10,
            "phone_number": "+1234567890",
            "is_primary": true,
            "label": "Home"
        }
    ]
}
```

### Example Error Response
```json
{
    "success": false,
    "detail": "Unauthorized"
}
```

### This endpoint:
1. Retrieves all phone numbers in a paginated manner
2. Ensures only authenticated users can access the data
3. Returns a list of phone numbers with their details

Ensure the user is authenticated to avoid access errors.
"""

GET_ALL_PHONES_OF_USER_DESCRIPTION="""
Retrieves all phone numbers of a user by user ID.

### Parameters
- `user_id (int)`: The ID of the user whose phone numbers are retrieved.
- `page (int)`: The page number for pagination.
- `limit (int, optional, default=10)`: The number of phone numbers per page.
- `db (AsyncSession)`: Database session for fetching phone numbers.
- `auth_obj (Optional[Dict[str, Any]])`: The authenticated user object.

### Returns
- `List[PhoneNumberResponse]`: A list of phone numbers associated with the user.

### Raises
- `HTTPException(401)`: If the user is not authenticated.
- `HTTPException(403)`: If the user does not have permission.

### Flow
1. Checks authentication status.
2. Fetches phone numbers associated with the user ID.
3. Returns the phone number list.

### Example Success Response
```json
{
    "success": true,
    "data": [
        {
            "id": 2,
            "user_id": 15,
            "phone_number": "+9876543210",
            "is_primary": false,
            "label": "Work"
        }
    ]
}
```

### Example Error Response
```json
{
    "success": false,
    "detail": "Unauthorized"
}
```

### This endpoint
1. Retrieves all phone numbers for a specific user in a paginated manner
2. Ensures only authenticated users can access the data
3. Returns a list of phone numbers with their details

Ensure the user is authenticated and the user_id is valid to avoid errors.
"""

CREATE_NEW_PHONE_DESCRIPTION="""
Creates a new phone number for the current user.

### Parameters
- `phone_body (PhoneNumberCreate)`: The phone number details to be created.
- `db (AsyncSession)`: Database session for inserting the phone number.
- `auth_obj (Optional[Dict[str, Any]])`: The authenticated user object.

### Returns
- `SuccessResponse`: Confirmation message.

### Raises
- `HTTPException(401)`: If the user is not authenticated.

### Flow
1. Checks authentication status.
2. Inserts a new phone number associated with the authenticated user.
3. Returns a success message.

### Example Success Response
```json
{
    "success": true,
    "message": "New phone number created successfully."
}
```

### Example Error Response
```json
{
    "success": false,
    "detail": "Unauthorized"
}
```

### This endpoint:
1. Creates a new phone number for the authenticated user
2. Ensures the provided data is valid
3. Returns the created phone number details

Ensure the user is authenticated and the phone number data is valid to avoid errors.
"""

UPDATE_PHONE_DESCRIPTION="""
Updates an existing phone number for the current user.

### Parameters
- `phone_id (int)`: The ID of the phone number to be updated.
- `phone_body (PhoneNumberUpdate)`: The updated phone number details.
- `db (AsyncSession)`: Database session for updating the phone number.
- `auth_obj (Optional[Dict[str, Any]])`: The authenticated user object.

### Returns
- `SuccessResponse`: Confirmation message.

### Raises
- `HTTPException(401)`: If the user is not authenticated.

### Flow
1. Checks authentication status.
2. Updates the phone number associated with the authenticated user.
3. Returns a success message.

### Example Success Response
```json
{
    "success": true,
    "message": "Phone number updated successfully."
}
```

### Example Error Response
```json
{
    "success": false,
    "detail": "Unauthorized"
}
```

### This endpoint:
1. Updates an existing phone number for the authenticated user
2. Ensures the phone number belongs to the user
3. Returns the updated phone number details

Ensure the user is authenticated and the phone_id is valid to avoid errors.
"""

DELETE_PHONE_DESCRIPTION="""
Deletes an existing phone number for the current user.

### Parameters
- `phone_id (int)`: The ID of the phone number to be deleted.
- `db (AsyncSession)`: Database session for deleting the phone number.
- `auth_obj (Optional[Dict[str, Any]])`: The authenticated user object.

### Returns
- `SuccessResponse`: Confirmation message.

### Raises
- `HTTPException(401)`: If the user is not authenticated.

### Flow
1. Checks authentication status.
2. Deletes the phone number associated with the authenticated user.
3. Returns a success message.

### Example Success Response
```json
{
    "success": true,
    "message": "Phone number deleted successfully."
}
```

### Example Error Response
```json
{
    "success": false,
    "detail": "Unauthorized"
}
```

### This endpoint:
1. Deletes an existing phone number for the authenticated user
2. Ensures the phone number belongs to the user
3. Returns a confirmation message

Ensure the user is authenticated and the phone_id is valid to avoid errors.
"""
