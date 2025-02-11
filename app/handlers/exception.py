import traceback
from fastapi import FastAPI, status, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
from pydantic import ValidationError

from app.services.log_service import LogService
from app.schemas.log_schema import LogLevel
from app.utils.logger import log
from app.helpers.log_helpers import log_helper


class LogStorageError(Exception):
    """Custom exception for log storage failures"""
    pass

class CustomException(Exception):
    "Custom exception for general usecases"
    pass

# ExceptionHandler class
class ExceptionHandler:
    def __init__(self, app: FastAPI):
        self.app = app
        self.logger = log
        self.register_exception_handlers()


    # Register the error handlers
    def register_exception_handlers(self):
        """Register all custom exception handlers."""
        self.app.add_exception_handler(StarletteHTTPException, self.http_exception_handler)
        self.app.add_exception_handler(RequestValidationError, self.validation_exception_handler)
        self.app.add_exception_handler(ValidationError, self.custom_validation_exception_handler)
        self.app.add_exception_handler(SQLAlchemyError, self.sqlalchemy_exception_handler)
        self.app.add_exception_handler(LogStorageError, self.log_storage_exception_handler)
        self.app.add_exception_handler(Exception, self.global_exception_handler)

    def format_exception_for_logging(self, exc: Exception) -> dict:
        """Format exception details for logging in a serializable format."""
        return {
            "type": exc.__class__.__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
            "args": getattr(exc, "args", ()),
            "details": {
                "status_code": getattr(exc, "status_code", None),
                "detail": getattr(exc, "detail", None)
            } if isinstance(exc, StarletteHTTPException) else None
        }

    # Helper function to store exception_logs in DB
    def log_exception(
        self,
        request: Request,
        exc: Exception,
        status_code: int = 500,
        level: LogLevel = LogLevel.ERROR,
        message: str = "Internal Server Error."
    ):
        """Helper method to log exceptions using the LogSchema."""
        try:
            # Extract request and exception details
            request_id = (
                request.state.request_id
                if hasattr(request.state, "request_id")
                else None
            )

            # Format the exception in a serializable way
            formatted_exception = self.format_exception_for_logging(exc)

            exception_details = log_helper.get_formatted_log_data(
                level=level,
                message=message,
                request_id=request_id,
                request=request,
                status=status_code,
                exception=formatted_exception
            )                                    

            # Save the log entry to the database
            LogService.create_log(exception_details)
            
        except Exception as e:
            self.logger.error(f"Failed to log exception: {str(e)}")

    async def http_exception_handler(self, request: Request, exc: StarletteHTTPException) -> JSONResponse:
        msg = f"HTTP Exception: {exc.detail}"
        self.logger.error(message=msg, extra=exc)
        self.log_exception(
            request=request,
            exc=exc,
            status_code=exc.status_code,
            message=msg,
            level=LogLevel.ERROR
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail, "error": "HTTP Error"},
        )

    async def validation_exception_handler(self, request: Request, exc: RequestValidationError) -> JSONResponse:
        msg = f"Validation Error: {exc.errors()}"
        self.logger.error(message=msg, extra=exc)
        self.log_exception(
            request=request,
            exc=exc,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=msg,
            level=LogLevel.WARNING
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": "Validation error",
                "errors": exc.errors(),
                "error": "Validation Error",
            },
        )

    async def custom_validation_exception_handler(self, request: Request, exc: ValidationError) -> JSONResponse:
        msg = f"Custom Validation Error: {str(exc)}"
        self.logger.error(message=msg, extra=exc)
        self.log_exception(
            request=request,
            exc=exc,
            status_code=status.HTTP_400_BAD_REQUEST,
            message=msg,
            level=LogLevel.WARNING
        )
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(exc), "error": "Custom Validation Error"},
        )
    
    async def sqlalchemy_exception_handler(self, request: Request, exc: SQLAlchemyError) -> JSONResponse:
        msg = f"Database Error: {str(exc)}"
        self.logger.critical(message=msg, extra=exc)
        self.log_exception(
            request=request,
            exc=exc,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=msg,
            level=LogLevel.ERROR
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "A database error occurred", "error": "Database Error"},
        )

    async def log_storage_exception_handler(self, request: Request, exc: LogStorageError) -> JSONResponse:
        # For log storage errors, we only use the logger since DB storage is failing
        self.logger.error(f"Log Storage Error: {str(exc)} - Path: {request.url.path}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Log storage failure", "error": "Log Storage Error"},
        )

    async def global_exception_handler(self, request: Request, exc: Exception) -> JSONResponse:
        msg = f"Custom Validation Error: {str(exc)}"
        self.logger.error(message=msg, extra=exc)
        await self.log_exception(
            request=request,
            exc=exc,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=msg,
            level=LogLevel.ERROR
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "An unexpected error occurred",
                "error": "Internal Server Error",
            },
        )