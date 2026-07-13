from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, Float, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, gen_uuid


class AIScore(Base):
    """AI scoring with pgvector support for embeddings."""
    __tablename__ = "ai_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    # submission_id: Mapped[str] = mapped_column(ForeignKey("submissions.id"), unique=True)
    submission_id: Mapped[str] = mapped_column(String(36), unique=True)  # Plain string until submissions table is defined

    skill_score: Mapped[float] = mapped_column(Float)
    experience_score: Mapped[float] = mapped_column(Float)
    domain_score: Mapped[float] = mapped_column(Float)
    project_score: Mapped[float] = mapped_column(Float)
    total_score: Mapped[float] = mapped_column(Float)

    # pgvector embedding for AI matching (1536 dimensions for OpenAI embeddings)
    # This will be used for semantic similarity matching
    embedding: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Will store as string, convert to vector in queries

    strengths: Mapped[str | None] = mapped_column(Text, nullable=True)
    weaknesses: Mapped[str | None] = mapped_column(Text, nullable=True)
    improvement_areas: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    calculated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # submission: Mapped["Submission"] = relationship(back_populates="ai_score")
