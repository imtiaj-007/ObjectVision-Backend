import time
from uuid import uuid4
from typing import Optional, Set, Dict, Any
import json

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.utils.logger import log
from app.helpers.log_helpers import log_helper
from app.schemas.log_schema import LogLevel
from app.services.log_service import LogService



class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Enhanced middleware for logging incoming requests and outgoing responses with detailed metadata.
    Features include performance tracking, error handling, request context, and security filtering.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[Set[str]] = None,
        exclude_prefixes: Optional[Set[str]] = None,
        exclude_methods: Optional[Set[str]] = None,
        slow_request_threshold: float = 1.0,
        sensitive_headers: Optional[Set[str]] = None,
        log_request_body: bool = True,
        max_body_size: int = 1024 * 100  # 100KB
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or {"/health", "/metrics", "/favicon.ico", "/docs", "/openapi.json"}
        self.exclude_prefixes = exclude_prefixes or {"/api/v1/files"}
        self.exclude_methods = exclude_methods or {"OPTIONS"}
        self.slow_request_threshold = slow_request_threshold
        self.sensitive_headers = sensitive_headers or {
            "authorization", "cookie", "x-api-key", "session", "csrf"
        }
        self.log_request_body = log_request_body
        self.max_body_size = max_body_size


    async def should_process_request(self, request: Request) -> bool:
        """Determine if the request should be processed based on exclusion rules."""
        if request.url.path in self.exclude_paths:
            return False
        if any(request.url.path.startswith(prefix) for prefix in self.exclude_prefixes):
            return False
        if request.method in self.exclude_methods:
            return False
        return True


    async def get_request_body(self, request: Request) -> Optional[Dict[str, Any]]:
        """Safely read and return the request body as JSON if enabled.
        
        Returns:
            Optional[Dict[str, Any]]: The parsed JSON body, or None if body logging is disabled.
            If there's an error or size limit exceeded, returns a dict with error information.
        """
        if not self.log_request_body:
            return None

        try:
            body = await request.body()
            if len(body) > self.max_body_size:
                return {
                    "error": "body_size_exceeded",
                    "message": f"Body size ({len(body)} bytes) exceeds maximum size",
                    "size": len(body)
                }
            
            # Try to parse as JSON
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return {
                    "error": "invalid_json",
                    "message": "Request body is not valid JSON",
                    "raw_content": body.decode()
                }
                
        except Exception as e:
            return {
                "error": "read_error",
                "message": f"Failed to read body: {str(e)}"
            }
            
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process the request and log relevant information."""
        if not await self.should_process_request(request):
            return await call_next(request)

        # Generate unique request ID and start timing
        start_time = time.perf_counter()
        request_id = str(uuid4())
        request.state.request_id = request_id

        try:
            # Log incoming request
            request_body = await self.get_request_body(request)            
            request_details = log_helper.get_formatted_log_data(
                LogLevel.INFO,
                f"Incoming request: {request.method} {request.url.path}",
                request_id=request_id,
                request=request,
                additional_details={"request_body": list(request_body.items())}
            )

            # Fixed: Use extra parameter for additional context
            log.info(
                message=f"Incoming request: {request.method} {request.url.path}",
                extra=request_details
            )            

            # Process request
            response = await call_next(request)
            duration = time.perf_counter() - start_time
            duration_ms = round(duration * 1000, 2)

            # Prepare response details
            log_level = LogLevel.ERROR if response.status_code >= 500 else LogLevel.WARNING if response.status_code >= 400 else LogLevel.INFO
            log_message = f"{'Server Error' if response.status_code >= 500 else 'Client Error' if response.status_code >= 400 else 'Request Completed'} : {request.method} {request.url.path}"
            res_details = log_helper.get_response_details(response)
            
            response_details = log_helper.get_formatted_log_data(
                level=log_level,
                message=log_message,
                request_id=request_id,
                request=request,
                status=response.status_code,
                duration=duration,
                additional_details=res_details
            )
            LogService.create_log(response_details)

            # Log response based on status code
            if response.status_code >= 500:
                log.error(
                    f"Server Error: {request.method} {request.url.path}",
                    extra=response_details
                )
            elif response.status_code >= 400:
                log.warning(
                    f"Client Error: {request.method} {request.url.path}",
                    extra=response_details
                )
            else:
                log.info(
                    f"Request Completed: {request.method} {request.url.path}",
                    extra=response_details
                )

            # Log performance metrics for slow requests
            msg = f"Slow Request Detected: {request.method} {request.url.path}"
            if duration > self.slow_request_threshold:
                performance_details = {
                    **response_details,
                    "message": msg,
                    "threshold": self.slow_request_threshold,
                    "threshold_exceeded_by": duration - self.slow_request_threshold
                }
                log.warning(
                    msg,
                    extra=performance_details
                )
                LogService.create_log(performance_details)

            return response

        except Exception as e:
            log.error(f"Unexpected exception occurred: {e}", extra=request_details)
            raise
