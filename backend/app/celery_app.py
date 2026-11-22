from celery import Celery
from .config import get_settings

settings = get_settings()
celery_app = Celery("diagnovision", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(task_serializer="json", result_serializer="json", timezone="UTC", beat_schedule={"scheduled-patient-analysis": {"task": "app.tasks.scheduled_analysis", "schedule": 86400.0}})

