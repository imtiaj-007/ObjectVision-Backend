import secrets
from urllib.parse import urlencode
from typing import Dict, Any, Annotated
from fastapi import APIRouter, Request, Response, Depends, HTTPException, status, Cookie
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.configuration.config import settings
from app.configuration.oauth import google_oauth
from app.db.database import db_session_manager

from app.services.auth_service import AuthService
from app.services.session_service import SessionService
from app.services.user_service import UserService

from app.schemas.user_schema import UserLogin, LogoutResponse, UserCreate
from app.schemas.auth_schema import SignupResponse
from app.schemas.token_schema import TokenResponse

from app.docs.descriptions import auth_desc
from app.docs.responses import auth_res


router = APIRouter()

@router.post(
    "/login", 
    response_model=TokenResponse, 
    status_code=status.HTTP_200_OK,
    responses=auth_res.LOGIN_RESPONSES,
    summary="User Login",
    description=auth_desc.LOGIN_DESCRIPTION
)
async def user_login(
    request: Request,
    response: Response,
    login_data: UserLogin,
    db: AsyncSession = Depends(db_session_manager.get_db),
) -> TokenResponse:
    """Authenticate user and manage session"""

    user = await AuthService.verify_user_credentials(db, login_data) 
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not verified, Please verify your account first."
        )
    current_session = await SessionService.get_user_session(db, user.id)

    try:
        # If user tries to login from new_device
        if login_data.new_device and current_session:
            await AuthService.logout_user(
                db=db, 
                user_id=user.id, 
                refresh_token=current_session.refresh_token, 
                all_devices=True
            )
            current_session = None

        return await SessionService.handle_user_session(request, response, db, user, login_data.remember_me, current_session)
    
    except HTTPException as http_error:
        if http_error.status_code == status.HTTP_401_UNAUTHORIZED:
            await AuthService.logout_user(db, user.id, None, True)
        raise http_error
    
    except Exception as e:
        raise


@router.post(
    "/signup", 
    response_model=SignupResponse, 
    status_code=status.HTTP_201_CREATED,
    responses=auth_res.SIGNUP_RESPONSES,
    summary="User Signup",
    description=auth_desc.SIGNUP_DESCRIPTION
)
async def user_signup(
    user: UserCreate, 
    db: AsyncSession = Depends(db_session_manager.get_db)
):
    """Authenticate user and manage session"""

    if not user.email or not user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and Password is required for sign-up"
        )
    return await UserService.create_user(db, user)


@router.get(
    "/oauth/google",
    status_code=status.HTTP_302_FOUND,
    responses=auth_res.GOOGLE_OAUTH_RESPONSES,
    summary="Initialize Google OAuth Flow",
    description=auth_desc.GOOGLE_OAUTH_DESCRIPTION
)
async def login_with_google(request: Request):
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
    

@router.get(
    "/oauth/google/callback",
    status_code=status.HTTP_200_OK,
    responses=auth_res.GOOGLE_OAUTH_CALLBACK_RESPONSES,
    summary="Google OAuth Callback Handler",
    description=auth_desc.GOOGLE_OAUTH_CALLBACK_DESCRIPTION
)
async def google_oauth_callback(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(db_session_manager.get_db)
):
    """Handle Google OAuth callback and fetch user info."""
    
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


@router.post(
    "/logout", 
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    responses=auth_res.LOGOUT_RESPONSES,
    summary="User Logout",
    description=auth_desc.LOGOUT_DESCRIPTION)
async def user_logout(
    response: Response,
    db: AsyncSession = Depends(db_session_manager.get_db),
    auth_obj: Dict[str, Any] = Depends(AuthService.authenticate_user),
    refresh_token: Annotated[str | None, Cookie()] = None,
    all_devices: bool = False
) -> Dict[str, Any]:
    """Logout user from current or all devices"""
    
    current_user = auth_obj["user"]
    current_token = auth_obj["token"]
    await AuthService.logout_user(db, current_user.id, current_token, refresh_token, all_devices)

    # Clear cookies
    response.delete_cookie("refresh_token")
    return {"message": "You have successfully logged out."}
