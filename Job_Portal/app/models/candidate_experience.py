from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, gen_uuid

if TYPE_CHECKING:
    from app.models.candidate import Candidate


class CandidateWorkExperience(Base):
    __tablename__ = "candidate_work_experiences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"), index=True)

    company_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(255))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    candidate: Mapped["Candidate"] = relationship(back_populates="work_experiences")


class CandidateProjectExperience(Base):
    __tablename__ = "candidate_project_experiences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"), index=True)

    project_title: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(255))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    domain: Mapped[str] = mapped_column(String(255))

    candidate: Mapped["Candidate"] = relationship(back_populates="project_experiences")


class CandidateEducation(Base):
    __tablename__ = "candidate_educations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"), index=True)

    degree: Mapped[str] = mapped_column(String(255))
    institute: Mapped[str] = mapped_column(String(255))
    passing_year: Mapped[int] = mapped_column(Integer)
    score: Mapped[str] = mapped_column(String(50))  # e.g. "85%" or "3.8 GPA"

    candidate: Mapped["Candidate"] = relationship(back_populates="educations")
