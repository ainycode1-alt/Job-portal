from __future__ import annotations

from app.models.base import Base, gen_uuid
from app.models.user import User
from app.models.client_profile import ClientProfile
from app.models.vendor_profile import VendorProfile
from app.models.otp_verification import OTPVerification
from app.models.refresh_token import RefreshToken
from app.models.password_reset_token import PasswordResetToken
from app.models.ai_score import AIScore
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.subscription import Subscription
from app.models.document import Document
from app.models.candidate_experience import (
    CandidateWorkExperience,
    CandidateProjectExperience,
    CandidateEducation,
)

__all__ = [
    "Base",
    "gen_uuid",
    "User",
    "ClientProfile",
    "VendorProfile",
    "OTPVerification",
    "RefreshToken",
    "PasswordResetToken",
    "AIScore",
    "Job",
    "Candidate",
    "Subscription",
    "Document",
    "CandidateWorkExperience",
    "CandidateProjectExperience",
    "CandidateEducation",
]
