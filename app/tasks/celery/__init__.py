from celery import Celery
from app.tasks.celery.celery_config import celery_settings

# Initialize Celery
celery_app = Celery("tasks")
celery_app.conf.update(celery_settings.celery_config)

celery_app.autodiscover_tasks(["app.tasks.taskfiles"])