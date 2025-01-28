import secrets
from urllib.parse import urlencode
from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.configuration.config import settings
from app.configuration.oauth import google_oauth

from app.db.database import db_session_manager
from app.services.auth_service import AuthService
from app.services.session_service import SessionService
from app.models.user_model import (
    UserLogin,
    TokenResponse,
)


router = APIRouter()

@router.post(
    "/login", 
    response_model=TokenResponse, 
    status_code=status.HTTP_200_OK
)
async def user_login(
    request: Request,
    response: Response,
    login_data: UserLogin,
    db: AsyncSession = Depends(db_session_manager.get_db),
    remember_me: bool = False,
    new_device: bool = False,
) -> TokenResponse:
    """Authenticate user and manage session"""
    try:
        user = await AuthService.authenticate_user(db, login_data) 
        return await SessionService.handle_user_session(
            request, 
            response, 
            db, 
            user, 
            remember_me, 
            new_device
        )

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        print(f"Unexpected error in user_login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while logging in",
        )

@router.get(
    "/oauth/google",
    status_code=status.HTTP_200_OK,
    responses={
        302: {"description": "Redirect to Google OAuth"},
        500: {"description": "Internal server error"},
    },
    summary="Initialize Google OAuth Flow",
    description="Creates a state token and redirects user to Google's OAuth 2.0 login page"
)
async def login_with_google(request: Request):
    try:
        """Create a state and Redirect user to Google's OAuth 2.0 login page."""
        state = secrets.token_urlsafe(32)
        request.session['oauth_state'] = state

        # Get the redirect URI from settings, fallback to request url if not set
        base_redirect_uri = settings.GOOGLE_REDIRECT_URI or str(request.url_for('google_auth_callback'))

        if not base_redirect_uri.startswith(('http://', 'https://')):
            scheme = request.headers.get('x-forwarded-proto', 'https')
            redirect_uri = f"{scheme}://{request.base_url.netloc}{base_redirect_uri}"
        else:
            redirect_uri = base_redirect_uri

        request.session['redirect_uri'] = redirect_uri

        return await google_oauth.authorize_redirect(
            request,
            redirect_uri,
            state=state
        )
    
    except Exception as e:
        print(f"Unexpected error in google_login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while logging in",
        )

@router.get(
    "/oauth/google/callback",
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Successfully authenticated with Google",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "token_type": "Bearer"
                    }
                }
            }
        },
        302: {
            "description": "Redirect to frontend with token or error",
            "headers": {
                "Location": {
                    "description": "URL to redirect to",
                    "schema": {"type": "string"}
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "State mismatch. Possible CSRF attack."
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An unexpected error occurred"
                    }
                }
            }
        }
    },
    summary="Google OAuth Callback Handler",
    description="""
    Handles the OAuth 2.0 callback from Google after user authorization.

    Parameters:
        request (Request): The incoming request object containing OAuth callback data
        response (Response): The response object for setting cookies
        db (AsyncSession): Database session for user operations
    
    Returns:
        RedirectResponse: Redirects to frontend with either:
            - Success: Frontend URL with access token in hash fragment
            - Error: Error page URL with error details in query parameters
            
    Raises:
        HTTPException(400): When state validation fails or missing parameters
        HTTPException(500): For unexpected server errors
        
    Security:
        - Validates state parameter to prevent CSRF attacks
        - Uses hash fragments for token transmission
        - Implements rate limiting
        - Validates redirect URIs
        
    Flow:
        1. Validates state parameter from session
        2. Exchanges authorization code for tokens
        3. Retrieves user info from Google
        4. Creates/updates user in database
        5. Generates application tokens
        6. Redirects to frontend
        
    Example Success Redirect:
        https://frontend.com/callback#access_token=xyz&token_type=Bearer&expires_in=3600
        
    Example Error Redirect:
        https://frontend.com/error?error=Invalid%20state%20parameter
    
    This endpoint:
    1. Validates the state parameter to prevent CSRF attacks
    2. Exchanges the authorization code for access tokens
    3. Retrieves user information from Google
    4. Creates or updates user in the database
    5. Generates application tokens
    6. Redirects to frontend with tokens
    
    The callback URL must be pre-registered in the Google OAuth Console.
    """
)
async def google_oauth_callback(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(db_session_manager.get_db)
):
    """Handle Google OAuth callback and fetch user info."""
    
    try:
        stored_state = request.session.get('oauth_state')
        request_state = request.query_params.get('state')

        # Verify state match
        if not stored_state or stored_state != request_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State mismatch. Possible CSRF attack."
            )
        
        redirect_uri = request.session.get('redirect_uri')
        if not redirect_uri:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing redirect URI"
            )

        # Clear the states from session
        request.session.pop('oauth_state', None)
        request.session.pop('redirect_uri', None)

        # Extract token information
        token = await google_oauth.authorize_access_token(request)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get access token"
            )
        
        try:
            userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
            res = await google_oauth.get(userinfo_url, token=token)
            user_info = res.json()

        except Exception as e:
            print(f"Token validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid token: {str(e)}"
            )

        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info"
            )

        token_response = await AuthService.handle_google_oauth(request, response, db, token, user_info)
        
        # Redirect to Frontend verification page or dashboard with hash fragments (more secure for tokens)
        token_params = urlencode(token_response)
        redirect_url = f"{settings.FRONTEND_SUCCESS_URL}#{token_params}"
        return RedirectResponse(
            url=redirect_url,
            status_code=status.HTTP_302_FOUND
        )
    
    except Exception as e:
        print(f"Unexpected error in google_login: {e}")
        redirect_url=f"{settings.FRONTEND_ERROR_URL}?error={str(e)}",
        return RedirectResponse(
            url=redirect_url,
            status_code=status.HTTP_302_FOUND
        )

@router.post(
    "/logout", 
    response_model=None,
    status_code=status.HTTP_200_OK
)
async def user_logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(db_session_manager.get_db),
    all_devices: bool = False
):
    """Logout user from current or all devices"""
    try:
        refresh_token = request.cookies.get("refresh_token")
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Bearer token missing or invalid"
            )
        
        access_token = auth_header[len("Bearer "):]
        current_user = await AuthService.get_current_user(db, access_token)
        await AuthService.logout_user(db, current_user.id, refresh_token, all_devices)

        # Clear cookies
        response.delete_cookie("refresh_token")
        return {"message": "You have successfully logged out."}

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        print(f"Unexpected error in user_logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while logging out",
        )