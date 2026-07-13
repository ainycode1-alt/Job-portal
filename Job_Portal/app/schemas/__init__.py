from __future__ import annotations

from app.schemas.auth import (
    RegisterStep1Request,
    RegisterStep1Response,
    VerifyOTPRequest,
    VerifyOTPResponse,
    CompleteRegistrationStep1Request,
    CompleteRegistrationStep2Request,
    CompleteRegistrationResponse,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from app.schemas.user import UserResponse, UserProfileResponse

__all__ = [
    "RegisterStep1Request",
    "RegisterStep1Response",
    "VerifyOTPRequest",
    "VerifyOTPResponse",
    "CompleteRegistrationStep1Request",
    "CompleteRegistrationStep2Request",
    "CompleteRegistrationResponse",
    "LoginRequest",
    "LoginResponse",
    "RefreshTokenRequest",
    "RefreshTokenResponse",
    "ForgotPasswordRequest",
    "ForgotPasswordResponse",
    "ResetPasswordRequest",
    "ResetPasswordResponse",
    "UserResponse",
    "UserProfileResponse",
]
