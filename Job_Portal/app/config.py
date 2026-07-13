from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    DATABASE_URL: str = Field(default="postgresql+asyncpg://jobportal:jobportal123@127.0.0.1:5433/job_portal")
    REDIS_URL: str = Field(default="redis://127.0.0.1:6379/0")

    SECRET_KEY: str = Field(default="e6b9e74ed9900027a9e3d047af10fee21706430f881acf57de50129e5d4a52cb")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    SMTP_HOST: str = Field(default="smtp.gmail.com")
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str = Field(default="ainycode1@gmail.com")
    SMTP_PASSWORD: str = Field(default="gdrw yzkd acvq higl")
    SMTP_FROM: str = Field(default="noreply@jobportal.com")

    OTP_EXPIRE_MINUTES: int = Field(default=10)
    OTP_MAX_ATTEMPTS: int = Field(default=5)
    OTP_RATE_LIMIT_PER_MINUTE: int = Field(default=3)

    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)

    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
