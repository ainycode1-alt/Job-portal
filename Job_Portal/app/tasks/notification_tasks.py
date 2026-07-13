from __future__ import annotations

from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.notification_tasks.send_push_notification")
def send_push_notification(user_id: str, title: str, message: str) -> bool:
    print(f"Push notification to {user_id}: {title} - {message}")
    return True


@celery_app.task(name="app.tasks.notification_tasks.send_sms")
def send_sms(phone_number: str, message: str) -> bool:
    print(f"SMS to {phone_number}: {message}")
    return True
