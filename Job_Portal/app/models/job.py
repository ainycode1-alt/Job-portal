from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Text, Date, DateTime, JSON, Boolean, Numeric, ForeignKey, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, gen_uuid, RichTextField, NumberField
from app.models.user import get_ist_now
from app.models.enums import LocationTypeEnum, EngagementTypeEnum

if TYPE_CHECKING:
    from app.models.client_profile import ClientProfile


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(NumberField, primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("client_profiles.id"), index=True)

    job_title: Mapped[str] = mapped_column(String(255))
    location: Mapped[str] = mapped_column(String(255))
    location_type: Mapped[LocationTypeEnum] = mapped_column(Enum(LocationTypeEnum))
    skills: Mapped[list] = mapped_column(JSON)  # List of required skills
    shift: Mapped[str] = mapped_column(String(50))  # IST / UST / PST / any

    # Hiring Details
    interview_rounds: Mapped[int] = mapped_column(Integer, default=1)
    positions: Mapped[int] = mapped_column(Integer, default=1)

    # Engagement Type
    engagement_type: Mapped[EngagementTypeEnum] = mapped_column(Enum(EngagementTypeEnum))

    # Qualification requirements
    experience: Mapped[str] = mapped_column(String(255))
    qualification: Mapped[str | None] = mapped_column(String(255), nullable=True)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    certifications: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Budget Information
    budget_currency: Mapped[str] = mapped_column(String(10), default="USD")
    budget_type: Mapped[str] = mapped_column(String(50))  # Hourly / Monthly / Yearly
    budget_min: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    budget_max: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    # Job Description
    jd_summary: Mapped[str | None] = mapped_column(RichTextField, nullable=True)

    # Project Timeline
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    project_duration: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Compliance and Insurance check requirements
    compliance_required: Mapped[bool] = mapped_column(Boolean, default=False)
    compliance_requirements: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=get_ist_now,
        server_default=func.timezone('Asia/Kolkata', func.now())
    )

    client: Mapped["ClientProfile"] = relationship(back_populates="jobs")
