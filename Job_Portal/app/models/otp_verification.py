from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, func, Boolean, Integer, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, gen_uuid, EmailField, NumberField
from app.models.enums import OTPPurposeEnum

if TYPE_CHECKING:
    from app.models.user import User


class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id: Mapped[int] = mapped_column(NumberField, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    email: Mapped[str] = mapped_column(EmailField, index=True)  # denormalized, useful for lookup before login

    otp_hash: Mapped[str] = mapped_column(String(255))
    purpose: Mapped[OTPPurposeEnum] = mapped_column(Enum(OTPPurposeEnum), default=OTPPurposeEnum.registration)

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0)       # max retry
    max_attempts: Mapped[int] = mapped_column(Integer, default=5)

    expires_at: Mapped[datetime] = mapped_column(DateTime)          # expiry
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="otp_verifications")
