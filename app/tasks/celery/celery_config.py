from typing import Tuple
from pydantic_settings import BaseSettings
from kombu import Queue
from app.configuration.config import settings


class CelerySettings(BaseSettings):
    BROKER_URL: str = settings.CELERY_BROKER_URL or "redis://localhost:6379/0"
    BACKEND_URL: str = settings.CELERY_BACKEND_URL or "redis://localhost:6379/0"

    # Define queues for different task types
    LOGGING_QUEUE: str = settings.LOGGING_QUEUE or "logging"
    TOKEN_QUEUE: str = settings.TOKEN_QUEUE or "token"
    EMAIL_QUEUE: str = settings.EMAIL_QUEUE or "email"

    task_queues: Tuple = (
        Queue(LOGGING_QUEUE, routing_key="logging.#"),
        Queue(TOKEN_QUEUE, routing_key="token.#"),
        Queue(EMAIL_QUEUE, routing_key="email.#"),
    )

    @property
    def celery_config(self):
        return {
            "broker_url": self.BROKER_URL,
            "result_backend": self.BACKEND_URL,
            "task_queues": self.task_queues,
            "task_routes": {
                "tasks.logging.*": {"queue": self.LOGGING_QUEUE},
                "tasks.token.*": {"queue": self.TOKEN_QUEUE},
                "tasks.email.*": {"queue": self.EMAIL_QUEUE},
            },
            "task_annotations": {
                "send_email_task": {"rate_limit": "100/m"},
                "store_log_entry": {"rate_limit": "1000/m"}
            },
            "task_serializer": "json",
            "accept_content": ["json"],
            "result_serializer": "json",
            "timezone": "UTC",
            "enable_utc": True,
            "task_track_started": True,
            "worker_send_task_events": True,
            "broker_connection_retry_on_startup": True,
        }


# Create a Global celery instance
celery_settings = CelerySettings()
