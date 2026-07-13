from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, Enum, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, gen_uuid
from app.models.enums import DocumentTypeEnum

if TYPE_CHECKING:
    from app.models.user import User


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)

    doc_type: Mapped[DocumentTypeEnum] = mapped_column(Enum(DocumentTypeEnum))
    file_url: Mapped[str] = mapped_column(String(500))
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)

    uploaded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="documents")
