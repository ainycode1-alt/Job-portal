from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import String, Integer, Text, Date, DateTime, JSON, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.job import Job
from app.models.base import Base, gen_uuid


class ClientProfile(Base):
    __tablename__ = "client_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True)

    company_name: Mapped[str] = mapped_column(String(255))
    gst_number: Mapped[str] = mapped_column(String(50))
    cin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    website_url: Mapped[str] = mapped_column(String(255))
    company_email: Mapped[str] = mapped_column(String(255))

    poc_name: Mapped[str] = mapped_column(String(255))
    poc_phone: Mapped[str] = mapped_column(String(20))
    poc_email: Mapped[str] = mapped_column(String(255))

    domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hq_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company_size: Mapped[str | None] = mapped_column(String(50), nullable=True)
    certifications: Mapped[list | None] = mapped_column(JSON, nullable=True)
    about_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    founded_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    linkedin_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    twitter_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    instagram_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    account_status: Mapped[str] = mapped_column(String(20), default="active")
    current_plan: Mapped[str | None] = mapped_column(String(50), nullable=True)
    plan_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="client_profile")
    jobs: Mapped[list["Job"]] = relationship(
        back_populates="client", cascade="all, delete-orphan"
    )
