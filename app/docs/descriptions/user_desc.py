CREATE_USER_DESCRIPTION = (
    description
) = """
Creates a new user in the system. This endpoint allows for both authenticated and unauthenticated requests to create a user.

### Parameters:
- **user (User Create):** The user data required to create a new user, including email and password.
- **db (AsyncSession):** Database session for user operations, automatically provided by FastAPI.
- **auth_obj (Optional[Dict[str, Any]]):** An optional authentication object that contains user information if the request is authenticated.

### Returns:
- **User Response:** Contains the details of the created user.

### Raises:
- `HTTPException(400)`: When the email or password is missing for unauthenticated requests.
- `HTTPException(403)`: When the authenticated user does not have admin or sub-admin privileges.

### Security:
- Validates user input for unauthenticated requests to ensure email and password are provided.
- Checks user roles for authenticated requests to ensure only authorized users can create new users.

### Flow:
1. Checks if the request is authenticated by examining the `auth_obj`.
2. If unauthenticated, validates that both email and password are provided.
3. If authenticated, verifies that the user has the necessary role (admin or sub-admin) to create a new user.
4. Calls the `User Service.create_user` method to create the user in the database and returns the user details.

### Example Success Response:
```json
{
    "id": 1,
    "email": "newuser@example.com",
    "created_at": "2023-10-01T12:00:00Z"
}
```

### Example Error Responses:
```json
example_1: {
    "detail": "Email and Password is required for sign-up"
}

example_2: {
    "detail": "Only admins can create users"
}
```

### This endpoint:
1. Allows unauthenticated users to sign up by providing email and password.
2. Allows authenticated users (admins/sub-admins) to create new users.
3. Returns the details of the created user upon successful creation.

Ensure that the user credentials are valid and that the authenticated user has the appropriate permissions to avoid errors.
"""