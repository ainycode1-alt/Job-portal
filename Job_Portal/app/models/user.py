from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, gen_uuid
from app.models.enums import RoleEnum, AccountStatusEnum, RegistrationStepEnum

if TYPE_CHECKING:
    from app.models.client_profile import ClientProfile
    from app.models.vendor_profile import VendorProfile
    from app.models.password_reset_token import PasswordResetToken
    from app.models.refresh_token import RefreshToken
    from app.models.subscription import Subscription
    from app.models.document import Document
    from app.models.otp_verification import OTPVerification


def get_ist_now() -> datetime:
    return datetime.now(timezone(timedelta(hours=5, minutes=30))).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum))

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    account_status: Mapped[AccountStatusEnum] = mapped_column(
        Enum(AccountStatusEnum), default=AccountStatusEnum.active
    )
    registration_step: Mapped[RegistrationStepEnum] = mapped_column(
        Enum(RegistrationStepEnum), default=RegistrationStepEnum.otp_pending
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=get_ist_now,
        server_default=func.timezone('Asia/Kolkata', func.now())
    )

    client_profile: Mapped["ClientProfile | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    vendor_profile: Mapped["VendorProfile | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    subscriptions: Mapped[list["Subscription"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    otp_verifications: Mapped[list["OTPVerification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
