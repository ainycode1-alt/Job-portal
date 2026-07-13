from __future__ import annotations

from celery import Celery
from app.config import settings

celery_app = Celery(
    "job_portal",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.services.email_service",
        "app.tasks.notification_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    worker_prefetch_multiplier=1,
    task_always_eager=settings.ENVIRONMENT == "development",
)
