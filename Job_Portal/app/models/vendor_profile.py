from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import String, Integer, Text, Date, DateTime, JSON, Boolean, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, gen_uuid, EmailField, URLField, RichTextField, NumberField

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.candidate import Candidate


class VendorProfile(Base):
    __tablename__ = "vendor_profiles"

    id: Mapped[int] = mapped_column(NumberField, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    company_name: Mapped[str] = mapped_column(String(255))
    gst_number: Mapped[str] = mapped_column(String(50))
    cin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    website_url: Mapped[str] = mapped_column(URLField)
    company_email: Mapped[str] = mapped_column(EmailField)

    poc_name: Mapped[str] = mapped_column(String(255))
    poc_phone: Mapped[int] = mapped_column(NumberField)
    poc_email: Mapped[str] = mapped_column(EmailField)

    tech_stack: Mapped[list | None] = mapped_column(JSON, nullable=True)
    hq_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company_size: Mapped[str | None] = mapped_column(String(50), nullable=True)
    certifications: Mapped[list | None] = mapped_column(JSON, nullable=True)
    about_summary: Mapped[str | None] = mapped_column(RichTextField, nullable=True)
    founded_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    has_labour_compliance: Mapped[bool] = mapped_column(Boolean, default=False)
    pf_registered: Mapped[bool] = mapped_column(Boolean, default=False)
    esic_registered: Mapped[bool] = mapped_column(Boolean, default=False)
    gmc_registered: Mapped[bool] = mapped_column(Boolean, default=False)
    fte_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Added fields
    vendor_model: Mapped[list | None] = mapped_column(JSON, nullable=True)
    compliance_checklist: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    declaration_confirmed: Mapped[bool | None] = mapped_column(Boolean, default=False, nullable=True)


    linkedin_url: Mapped[str | None] = mapped_column(URLField, nullable=True)
    twitter_url: Mapped[str | None] = mapped_column(URLField, nullable=True)
    instagram_url: Mapped[str | None] = mapped_column(URLField, nullable=True)
    facebook_url: Mapped[str | None] = mapped_column(URLField, nullable=True)

    account_status: Mapped[str] = mapped_column(String(20), default="active")
    current_plan: Mapped[str | None] = mapped_column(String(50), nullable=True)
    plan_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)

    user: Mapped["User"] = relationship(back_populates="vendor_profile")
    candidates: Mapped[list["Candidate"]] = relationship(
        back_populates="vendor", cascade="all, delete-orphan"
    )
