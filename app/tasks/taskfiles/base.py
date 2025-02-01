from celery import Task
from app.performance.metrics import metrics

class BaseTask(Task):
    """Base task with common functionality"""
    abstract = True
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print(exc, task_id, args, einfo)
        # metrics.task_failures.labels(
        #     task_type=self.name
        # ).inc()
        # super().on_failure(exc, task_id, args, kwargs, einfo)