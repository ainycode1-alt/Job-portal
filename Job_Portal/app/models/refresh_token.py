from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, gen_uuid

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)

    token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    device_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)

    replaced_by_token_id: Mapped[str | None] = mapped_column(
        ForeignKey("refresh_tokens.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")
