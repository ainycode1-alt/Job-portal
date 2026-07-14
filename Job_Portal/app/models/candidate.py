from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, JSON, ForeignKey, func, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, gen_uuid, URLField, NumberField
from app.models.user import get_ist_now

if TYPE_CHECKING:
    from app.models.vendor_profile import VendorProfile
    from app.models.candidate_experience import (
        CandidateWorkExperience,
        CandidateProjectExperience,
        CandidateEducation,
    )


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(NumberField, primary_key=True, autoincrement=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendor_profiles.id"), index=True)

    full_name: Mapped[str] = mapped_column(String(255))
    gender: Mapped[str] = mapped_column(String(20))
    designation: Mapped[str] = mapped_column(String(255))
    total_experience: Mapped[float] = mapped_column(Numeric(4, 1))  # e.g. 10.5 years

    # Work Preferences
    deployment_type: Mapped[str] = mapped_column(String(50))  # Onsite / Hybrid / Remote
    availability: Mapped[str] = mapped_column(String(50))  # Immediate / Notice period
    engagement_types: Mapped[list] = mapped_column(JSON)  # e.g., ["Full-time", "C2C"]

    # Skills
    primary_skills: Mapped[list] = mapped_column(JSON)  # List of core technical skills
    secondary_skills: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Location (Mandatory for fulltime requirements)
    state: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100))

    certifications: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Social links
    linkedin_url: Mapped[str | None] = mapped_column(URLField, nullable=True)
    github_url: Mapped[str | None] = mapped_column(URLField, nullable=True)

    # Candidate Rate Details
    rate_currency: Mapped[str] = mapped_column(String(10), default="USD")
    rate_type: Mapped[str] = mapped_column(String(50))  # Hourly / Monthly / Yearly
    rate_min: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    rate_max: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=get_ist_now,
        server_default=func.timezone('Asia/Kolkata', func.now())
    )

    vendor: Mapped["VendorProfile"] = relationship(back_populates="candidates")

    # History relationships
    work_experiences: Mapped[list["CandidateWorkExperience"]] = relationship(
        back_populates="candidate", cascade="all, delete-orphan"
    )
    project_experiences: Mapped[list["CandidateProjectExperience"]] = relationship(
        back_populates="candidate", cascade="all, delete-orphan"
    )
    educations: Mapped[list["CandidateEducation"]] = relationship(
        back_populates="candidate", cascade="all, delete-orphan"
    )
