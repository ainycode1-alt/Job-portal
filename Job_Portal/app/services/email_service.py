from __future__ import annotations

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.services.email_service.send_email")
def send_email_task(to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
    try:
        msg = MIMEMultipart()
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to_email
        msg["Subject"] = subject

        content_type = "html" if is_html else "plain"
        msg.attach(MIMEText(body, content_type))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


def send_otp_email(email: str, otp: str, purpose: str = "registration") -> None:
    subject = f"Your OTP for {purpose.replace('_', ' ').title()}"
    body = f"""
    <html>
    <body>
        <h2>Job Portal Verification</h2>
        <p>Your OTP code is: <strong style="font-size: 24px; color: #2d6cdf;">{otp}</strong></p>
        <p>This OTP will expire in 10 minutes.</p>
        <p>If you did not request this, please ignore this email.</p>
    </body>
    </html>
    """
    send_email_task.delay(email, subject, body, is_html=True)


def send_password_reset_email(email: str, otp: str) -> None:
    subject = "Password Reset OTP"
    body = f"""
    <html>
    <body>
        <h2>Password Reset Request</h2>
        <p>Your password reset OTP is: <strong style="font-size: 24px; color: #e74c3c;">{otp}</strong></p>
        <p>This OTP will expire in 10 minutes.</p>
        <p>If you did not request a password reset, please ignore this email.</p>
    </body>
    </html>
    """
    send_email_task.delay(email, subject, body, is_html=True)
