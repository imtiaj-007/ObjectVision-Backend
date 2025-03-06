from typing import Tuple, Dict, Any
from datetime import datetime
from pydantic_settings import BaseSettings
from kombu import Queue
import msgpack
from app.configuration.config import settings


def custom_encode(obj):
    """Custom Msgpack encoder to handle datetime serialization"""
    if isinstance(obj, datetime):
        return {"__datetime__": obj.isoformat()}
    return obj

def custom_decode(obj):
    """Custom Msgpack decoder to handle datetime deserialization"""
    if "__datetime__" in obj:
        return datetime.fromisoformat(obj["__datetime__"])
    return obj

custom_msgpack = {
    "dumps": lambda obj: msgpack.packb(obj, default=custom_encode, use_bin_type=True),
    "loads": lambda obj: msgpack.unpackb(obj, object_hook=custom_decode, raw=False),
}


class CelerySettings(BaseSettings):
    # Broker and Backend Configuration
    BROKER_URL: str = settings.CELERY_BROKER_URL or "redis://localhost:6379/0"
    BACKEND_URL: str = settings.CELERY_BACKEND_URL or "redis://localhost:6379/0"

    # Queues for different task types
    LOGGING_QUEUE: str = settings.LOGGING_QUEUE or "logging"
    TOKEN_QUEUE: str = settings.TOKEN_QUEUE or "token"
    EMAIL_QUEUE: str = settings.EMAIL_QUEUE or "email"
    DETECTION_QUEUE: str = settings.DETECTION_QUEUE or "detection"
    SUBSCRIPTION_QUEUE: str = settings.SUBSCRIPTION_QUEUE or "subscription"

    # Task Queues with Priorities
    task_queues: Tuple = (
        Queue(LOGGING_QUEUE,routing_key="logging.#",queue_arguments={"x-max-priority": 10},),
        Queue(TOKEN_QUEUE, routing_key="token.#", queue_arguments={"x-max-priority": 10}),
        Queue(EMAIL_QUEUE, routing_key="email.#", queue_arguments={"x-max-priority": 10}),
        Queue(DETECTION_QUEUE,routing_key="detection.#",queue_arguments={"x-max-priority": 10}),
        Queue(SUBSCRIPTION_QUEUE,routing_key="subscription.#",queue_arguments={"x-max-priority": 10}),
    )

    # Task Annotations with Rate Limits, Retries, and Priorities
    task_annotations: Dict[str, Dict[str, Any]] = {
        "store_log_entry": {
            "rate_limit": "1000/m",
            "max_retries": 3,
            "retry_delay": 30,
            "priority": 2,
        },
        "send_email_task": {
            "rate_limit": "100/m",
            "max_retries": 3,
            "retry_delay": 60,
            "priority": 7,
        },
        "send_otp_email_task": {
            "rate_limit": "100/m",
            "max_retries": 3,
            "retry_delay": 60,
            "priority": 8,
        },
        "send_plan_purchase_email_task": {
            "rate_limit": "100/m",
            "max_retries": 3,
            "retry_delay": 60,
            "priority": 7,
        },
        "send_subscription_email_task": {
            "rate_limit": "100/m",
            "max_retries": 3,
            "retry_delay": 60,
            "priority": 8,
        },
        "send_welcome_email_task": {
            "rate_limit": "100/m",
            "max_retries": 3,
            "retry_delay": 60,
            "priority": 7,
        },
        "send_password_reset_email_task": {
            "rate_limit": "100/m",
            "max_retries": 3,
            "retry_delay": 60,
            "priority": 7,
        },
        "blacklist_token_task": {
            "rate_limit": "100/m",
            "max_retries": 3,
            "retry_delay": 60,
            "priority": 6,
        },
        "store_data_in_db_task": {
            "rate_limit": "100/m",
            "max_retries": 3,
            "retry_delay": 30,
            "priority": 8,
        },
        "store_order_task": {
            "rate_limit": "100/m",
            "max_retries": 3,
            "retry_delay": 30,
            "priority": 8,
        },
    }

    @property
    def celery_config(self) -> Dict[str, Any]:
        """Generate the Celery configuration dictionary."""
        return {
            "broker_url": self.BROKER_URL,
            "result_backend": self.BACKEND_URL,
            "task_queues": self.task_queues,
            "task_routes": {
                "tasks.logging.*": {"queue": self.LOGGING_QUEUE},
                "tasks.token.*": {"queue": self.TOKEN_QUEUE},
                "tasks.email.*": {"queue": self.EMAIL_QUEUE},
                "tasks.detection.*": {"queue": self.DETECTION_QUEUE},
                "tasks.subscription.*": {"queue": self.SUBSCRIPTION_QUEUE},
            },
            "task_annotations": self.task_annotations,        
            "timezone": "UTC",
            "enable_utc": True,
            "task_track_started": True,
            "task_time_limit": 300,
            "worker_concurrency": 4,
            "worker_send_task_events": True,
            "worker_log_format": "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
            "worker_redirect_stdouts": True,
            "broker_connection_retry_on_startup": True,
            "task_default_priority": 5,
            "worker_prefetch_multiplier": 1,
            "task_serializer": "msgpack",
            "event_serializer": "msgpack",
            "result_serializer": "msgpack",
            "serializer": "msgpack",
            "accept_content": ["msgpack", "json"],
            "result_accept_content": ["msgpack", "json"],
        }


# Global Celery instance
celery_settings = CelerySettings()
