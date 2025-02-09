LOGIN_DESCRIPTION = (
    description
) = """
Authenticates the user and manages the session. This endpoint allows users to log in by providing their credentials.

### Parameters:
- **request (Request):** The incoming request object for the login operation
- **response (Response):** The response object for setting cookies or headers
- **login_data (User Login):** The user's login credentials (username and password)
- **remember_me (bool):** Optional; if true, the session will persist beyond the current browser session
- **new_device (bool):** Optional; if true, indicates that the user is logging in from a new device
- **db (AsyncSession):** Database session for user operations

### Returns:
- **TokenResponse:** Contains the access token and other session-related information

### Raises:
- `HTTPException(400):` When the provided credentials are invalid
- `HTTPException(401):` When the user is not authorized
- `HTTPException(409):` When the user is logged in with another device
- `HTTPException(500):` For unexpected server errors


### Security:
- Validates user credentials against the database
- Manages sessions securely, including handling new device logins
    
### Flow:
1. Verifies user credentials using the provided login data
2. Retrieves the current user session from the database
3. If logging in from a new device, logs out the user from all devices if a session exists
4. Handles user session creation or update, returning the access token and session details
    
### Example Success Response:
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "Bearer",
    "expires_in": 3600
}
```
    
### Example Error Response:
```json
{
    "detail": "Invalid username or password"
}
```

### This endpoint:
1. Authenticates the user based on provided credentials
2. Manages user sessions, including handling new device logins
3. Returns an access token for authenticated users

Ensure that the user credentials are correct to avoid authentication errors.
"""

SIGNUP_DESCRIPTION = (
    description
) = """
Registers a new user and creates their account. This endpoint allows users to sign up by providing their email and password.

### Parameters:
- **user (UserCreate):** The user's sign-up data, including email and password
- **db (AsyncSession):** Database session for creating the user

### Returns:
- **SignupResponse:** Contains the created user's information and a success message

### Raises:
- `HTTPException(400):` When the provided data is invalid (e.g., missing email or password)
- `HTTPException(409):` When the email already exists in the system (conflict)
- `HTTPException(500):` For unexpected server errors

### Security:
- Ensures the user does not already exist in the system
- Safely stores the user's password using encryption techniques

### Flow:
1. Validates the user-provided data (email and password)
2. Checks if the email is already in use by another user
3. Creates a new user in the database with the provided credentials
4. Returns the newly created user details

### Example Success Response:
```json
{
  "status": 1,
  "message": "User registration successful",
  "user_id": 1,
  "email": "user@example.com"
}
```

### Example Error Response:
```json
{
    "detail": "Email and Password is required for sign-up"
}
```

### This endpoint:
1. Registers a new user by creating an account with the provided credentials
2. Ensures the email is not already associated with an existing account
3. Returns a success message along with the user's details

Ensure the email is unique and password meets the required criteria to avoid errors during registration.
"""

GOOGLE_OAUTH_DESCRIPTION = (
    description
) = """
Initiates the OAuth 2.0 flow by creating a state token and redirecting the user to Google's OAuth 2.0 login page.

### Parameters:
- **request (Request):** The incoming request object for initiating the OAuth flow
- **response (Response):** The response object for setting cookies
- **db (AsyncSession):** Database session for state token storage

### Returns:
- **RedirectResponse:** Redirects to Google's OAuth 2.0 login page with the state token

### Raises:
- `HTTPException(500):` For unexpected server errors
    
### Security:
- Generates a unique state token to prevent CSRF attacks
- Stores the state token in the session for validation during callback
    
### Flow:
1. Generates a unique state token
2. Stores the state token in the session
3. Constructs the authorization URL for Google OAuth
4. Redirects the user to the Google OAuth login page
    
### Example Redirect:
[Google OAuth v2 API URL](https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=https://yourapp.com/oauth/google/callback&state=STATE_TOKEN&scope=openid%20email%20profile)

### This endpoint:
1. Generates a unique state token to prevent CSRF attacks
2. Stores the state token in the session for later validation
3. Redirects the user to Google's OAuth 2.0 login page for authentication

Ensure that the redirect URI is pre-registered in the Google OAuth Console.
"""

GOOGLE_OAUTH_CALLBACK_DESCRIPTION = (
    description
) = """
Handles the OAuth 2.0 callback from Google after user authorization.

### Parameters:
- **request (Request):** The incoming request object containing OAuth callback data
- **response (Response):** The response object for setting cookies
- **db (AsyncSession):** Database session for user operations

### Returns:
- **RedirectResponse:** Redirects to frontend with either:
    - `Success:` Frontend URL with access token in hash fragment
    - `Error:` Error page URL with error details in query parameters
        
### Raises:
- `HTTPException(400):` When state validation fails or missing parameters
- `HTTPException(500):` For unexpected server errors
    
### Security:
- Validates state parameter to prevent CSRF attacks
- Uses hash fragments for token transmission
- Implements rate limiting
- Validates redirect URIs
    
### Flow:
1. Validates state parameter from session
2. Exchanges authorization code for tokens
3. Retrieves user info from Google
4. Creates/updates user in database
5. Generates application tokens
6. Redirects to frontend
    
### Example Success Redirect:
    https://frontend.com/callback#access_token=xyz&token_type=Bearer&expires_in=3600
    
### Example Error Redirect:
    https://frontend.com/error?error=Invalid%20state%20parameter

### This endpoint:
1. Validates the state parameter to prevent CSRF attacks
2. Exchanges the authorization code for access tokens
3. Retrieves user information from Google
4. Creates or updates user in the database
5. Generates application tokens
6. Redirects to frontend with tokens

The callback URL must be pre-registered in the Google OAuth Console.
"""

LOGOUT_DESCRIPTION = (
    description
) = """
Logs out the user from the current session or all devices. This endpoint allows users to terminate their session securely.

### Parameters:
- **response (Response):** The response object for setting cookies or headers
- **db (AsyncSession):** Database session for user operations
- **auth_obj (Dict[str, Any]):** The authenticated user object obtained from the authentication service
- **refresh_token (str | None):** Optional; the refresh token stored in cookies for session management
- **all_devices (bool):** Optional; if true, logs the user out from all devices

### Returns:
- Dict[str, Any]: A message indicating the logout status

### Raises:
- `HTTPException(401):` When the user is not authorized
- `HTTPException(500):` For unexpected server errors
    
### Security:
- Validates the user's authentication status before logging out
- Clears the refresh token from cookies to prevent further access
    
### Flow:
1. Authenticates the user using the provided authentication object
2. Calls the logout service to terminate the user session
3. Clears the refresh token cookie from the response
4. Returns a success message indicating the user has logged out
    
### Example Success Response:
```json
{
    "message": "You have successfully logged out."
}
```
    
### Example Error Response:
```json
{
    "detail": "User  is not authorized"
}
```

### This endpoint:
1. Logs out the user from the current session or all devices based on the provided parameters
2. Clears the refresh token to ensure the user cannot access protected resources
3. Returns a confirmation message upon successful logout

Ensure that the user is authenticated before attempting to log out.
"""
