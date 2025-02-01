from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class LogLevel(str, Enum):
    """
    Enum representing different log levels.
    """

    INFO = "INFO"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    DEBUG = "DEBUG"
    CRITICAL = "CRITICAL"


class LogBase(BaseModel):
    """
    Base Pydantic model for log schema.
    """

    level: LogLevel = Field(
        ..., description="Log level indicating severity", example="ERROR"
    )
    message: str = Field(
        ..., description="Detailed log message", example="Database connection failed"
    )
    timestamp: Optional[datetime] = Field(
        None, description="Time when the log was created", example=""
    )


class LogCreate(LogBase):
    """
    Pydantic model for creating a log entry.
    """

    request_id: Optional[str] = Field(
        None,
        description="Unique identifier for the request",
        example="123e4567-e89b-12d3-a456-426614174000",
    )
    client_host: Optional[str] = Field(
        None, max_length=255, description="Client IP address", example="192.168.1.1"
    )
    client_port: Optional[int] = Field(
        None, description="Client port number", example=443
    )
    method: Optional[str] = Field(
        None, max_length=10, description="HTTP method used", example="POST"
    )
    path: Optional[str] = Field(
        None, max_length=2048, description="API endpoint path", example="/api/v1/login"
    )
    query_params: Optional[Dict[str, Any]] = Field(
        None,
        description="Query parameters sent with the request",
        example={"search": "pydantic"},
    )
    headers: Optional[Dict[str, Any]] = Field(
        None, description="Request headers", example={"User-Agent": "Mozilla/5.0"}
    )
    status_code: Optional[int] = Field(
        None, description="HTTP response status code", example=200
    )
    error_details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details",
        example={"error": "Database timeout"},
    )
    stack_trace: Optional[str] = Field(
        None,
        description="Stack trace for debugging",
        example="Traceback (most recent call last): ...",
    )
    duration: Optional[float] = Field(
        None, description="Time taken to process the request in seconds", example=1.23
    )
    additional_details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata",
        example={"user_id": "42", "role": "admin"},
    )
    

class LogResponse(LogBase):
    """
    Pydantic model for responding with a log entry.
    """

    id: int = Field(
        ..., description="Unique identifier for the log entry", example=1001
    )
    request_id: Optional[str] = Field(
        None,
        description="Unique identifier for the request",
        example="123e4567-e89b-12d3-a456-426614174000",
    )
    client_host: Optional[str] = Field(
        None, max_length=255, description="Client IP address", example="192.168.1.1"
    )
    client_port: Optional[int] = Field(
        None, description="Client port number", example=443
    )
    method: Optional[str] = Field(
        None, max_length=10, description="HTTP method used", example="POST"
    )
    path: Optional[str] = Field(
        None, max_length=2048, description="API endpoint path", example="/api/v1/login"
    )
    query_params: Optional[Dict[str, Any]] = Field(
        None,
        description="Query parameters sent with the request",
        example={"search": "pydantic"},
    )
    headers: Optional[Dict[str, Any]] = Field(
        None, description="Request headers", example={"User-Agent": "Mozilla/5.0"}
    )
    status_code: Optional[int] = Field(
        None, description="HTTP response status code", example=500
    )
    error_details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details",
        example={"error": "Database timeout"},
    )
    stack_trace: Optional[str] = Field(
        None,
        description="Stack trace for debugging",
        example="Traceback (most recent call last): ...",
    )
    duration: Optional[float] = Field(
        None, description="Time taken to process the request in seconds", example=1.23
    )
    additional_details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata",
        example={"user_id": "42", "role": "admin"},
    )
    
