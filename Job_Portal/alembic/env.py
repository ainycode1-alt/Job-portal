from __future__ import annotations

import os
from logging.config import fileConfig

from sqlalchemy import create_engine, pool, text

from alembic import context

from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jobportal:jobportal123@localhost:5433/job_portal")
SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

from app.models.base import Base

from app.models.user import User
from app.models.client_profile import ClientProfile
from app.models.vendor_profile import VendorProfile
from app.models.otp_verification import OTPVerification
from app.models.refresh_token import RefreshToken
from app.models.password_reset_token import PasswordResetToken
from app.models.ai_score import AIScore
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.subscription import Subscription
from app.models.document import Document
from app.models.candidate_experience import (
    CandidateWorkExperience,
    CandidateProjectExperience,
    CandidateEducation,
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = SYNC_DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        SYNC_DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        connection.commit()
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()
        connection.commit()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
