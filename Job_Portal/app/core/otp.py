from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from app.config import settings


def generate_otp(length: int = 4) -> str:
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


def get_otp_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)


def is_otp_expired(expires_at: datetime) -> bool:
    return datetime.now(timezone.utc) > expires_at
