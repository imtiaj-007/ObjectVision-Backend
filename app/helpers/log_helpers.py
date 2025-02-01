import traceback
from fastapi import Request, Response
from typing import Optional, Any, Dict, List, Set
from app.schemas.log_schema import LogLevel


class LogHelper:
    """
    Standardized logging helper for FastAPI applications with enhanced error handling
    and request tracking capabilities.
    """    

    def __init__(self, **kwargs: Any):

        self.SAFE_REQUEST_HEADERS: Set[str] = frozenset({   
            "user-agent",
            "referer",
            "x-request-id",
            "accept",
            "accept-encoding",
            "accept-language",
            "x_forwarded_for"
        })
        self.SAFE_RESPONSE_HEADERS: Set[str] = frozenset({   
            "content-encoding",
            "content-language",
            "content-length",
            "content-type",
        })
        self.extra = kwargs

    def get_request_details(self, request: Request) -> Dict[str, Any]:
        """
        Extract relevant request details for logging with optional header filtering.
        
        Args:
            request: FastAPI Request object
            
        Returns:
            Dict[str, Any]: Filtered request details
        """               
        request_details = {
            "method": request.method,
            "path": request.url.path,
            "query_params": request.query_params,  
            "client_host": request.client.host if request.client else None,
            "client_port": request.client.port if request.client else None
        }

        # Extract safe headers
        headers = {
            key.lower(): request.headers.get(key)
            for key in self.SAFE_REQUEST_HEADERS
            if request.headers.get(key) is not None
        }
        
        if headers:
            request_details["headers"] = headers

        return request_details

    def get_response_details(self, response: Response) -> Dict[str, Any]:
        """
        Extract relevant request details for logging with optional header filtering.
        
        Args:
            request: FastAPI Request object
            
        Returns:
            Dict[str, Any]: Filtered request details
        """               

        # Extract safe headers
        response_details = {
            key.lower(): response.headers.get(key)
            for key in self.SAFE_RESPONSE_HEADERS
            if response.headers.get(key) is not None
        }    

        return response_details


    def get_formatted_log_data(
        self,
        level: LogLevel,
        message: str,
        request_id: Optional[str] = None,
        request: Optional[Request] = None,
        status: Optional[int] = None,
        duration: Optional[float] = None,
        additional_details: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None
    ) -> Dict[str, Any]:
        """
        Constructs a dictionary of log data according to LogSchema format.
        
        Args:
            level: LogLevel enum indicating severity
            message: Main log message
            request_id: Optional request identifier
            request: Optional FastAPI request object for request context
            duration: Optional execution duration in seconds
            additional_details: Optional dictionary of additional data
            exception: Optional exception object for error details
            
        Returns:
            Dict[str, Any]: Formatted log data
        """
        if not isinstance(level, LogLevel):
            try:
                level = LogLevel[level] if isinstance(level, str) else LogLevel.ERROR
            except (KeyError, TypeError):
                level = LogLevel.ERROR
        
        log_data = {
            "level": level.name,
            "message": message,
            "request_id": request_id,
            "status_code": status,
            "duration": round(duration, 3) if duration is not None else None
        }

        # Add request context if available
        if request:
            request_data = self.get_request_details(request)               
            log_data.update(**request_data)
        
        # Add exception details if available
        if exception:
            error_details = {
                "type": type(exception).__name__,
                "message": str(exception),
                "args": getattr(exception, 'args', None),                
            }
            log_data["error_details"] = error_details

            stack_trace = "".join(
                traceback.format_exception(type(exception), exception, exception.__traceback__)
            )
            log_data["stack_trace"] = stack_trace or None
        
        # Add any additional details
        if additional_details:
            log_data["additional_details"] = additional_details

        return log_data

    def process_validation_errors(self, errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process validation errors into a standardized format.
        
        Args:
            errors: List of validation error dictionaries
            
        Returns:
            List[Dict[str, Any]]: Processed validation errors
        """
        return [{
            "location": " -> ".join(str(loc) for loc in error.get("loc", [])),
            "message": error.get("msg", "Unknown validation error"),
            "type": error.get("type", "unknown_error"),
            "input": error.get("input", None)
        } for error in errors]    


# Create an instance globally
log_helper = LogHelper()