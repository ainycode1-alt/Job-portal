from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Date, DateTime, Boolean, Enum, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, gen_uuid, NumberField
from app.models.enums import SubscriptionPlanEnum, SubscriptionStatusEnum

if TYPE_CHECKING:
    from app.models.user import User


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(NumberField, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    plan: Mapped[SubscriptionPlanEnum] = mapped_column(Enum(SubscriptionPlanEnum))
    status: Mapped[SubscriptionStatusEnum] = mapped_column(
        Enum(SubscriptionStatusEnum), default=SubscriptionStatusEnum.active
    )
    is_trial: Mapped[bool] = mapped_column(Boolean, default=False)

    started_at: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    expires_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="subscriptions")
