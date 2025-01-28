from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.configuration.security import SecurityConfig


open_paths = [
    "/docs", 
    "/redoc",
    "/openapi.json", 
    "/health"
]

class AuthenticateUserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        
        # Skip authentication for public routes
        public_paths = open_paths
        if request.url.path in public_paths:
            return await call_next(request)

        # Extract token from headers
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"detail": "Authentication token missing or invalid"}, 
                status_code=401
            )

        token = auth_header.split(" ")[1]
        # Validate the token
        user = SecurityConfig.verify_token(token)
        if not user:
            return JSONResponse(
                {"detail": "Invalid or expired token"}, 
                status_code=401
            )

        # Attach user information to the request state
        request.state.user = user
        return await call_next(request)
