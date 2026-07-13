from __future__ import annotations

import re
from datetime import datetime
from typing import Literal, Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator, BeforeValidator

from app.models.user import RoleEnum


GSTIN_REGEX = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$"

STATE_CODES = {
    "01": "Jammu & Kashmir", "02": "Himachal Pradesh", "03": "Punjab",
    "04": "Chandigarh", "05": "Uttarakhand", "06": "Haryana",
    "07": "Delhi", "08": "Rajasthan", "09": "Uttar Pradesh",
    "10": "Bihar", "11": "Sikkim", "12": "Arunachal Pradesh",
    "13": "Nagaland", "14": "Manipur", "15": "Mizoram",
    "16": "Tripura", "17": "Meghalaya", "18": "Assam",
    "19": "West Bengal", "20": "Jharkhand", "21": "Odisha",
    "22": "Chhattisgarh", "23": "Madhya Pradesh", "24": "Gujarat",
    "27": "Maharashtra", "29": "Karnataka", "30": "Goa",
    "31": "Lakshadweep", "32": "Kerala", "33": "Tamil Nadu",
    "34": "Puducherry", "36": "Telangana", "37": "Andhra Pradesh",
}


def validate_gst_number(v: str) -> str:
    gst = v.strip().upper()
    if not re.fullmatch(GSTIN_REGEX, gst):
        raise ValueError(f"Invalid GST format: {gst}")
    
    state_code = gst[:2]
    if state_code not in STATE_CODES:
        raise ValueError(f"Invalid GST state code: {state_code}")
        
    return gst


CIN_REGEX = r"^[LU][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}$"

CIN_STATE_CODES = {
    "AN", "AP", "AR", "AS", "BR", "CH", "CG", "CT", "DN", "DL", "GA", "GJ", "HR", "HP",
    "JK", "JH", "KA", "KL", "LA", "LD", "MP", "MH", "MN", "ML", "MZ", "NL", "OR", "OD",
    "PY", "PB", "RJ", "SK", "TN", "TG", "TS", "TR", "UP", "UA", "UR", "UT", "WB"
}


def validate_cin_number(v: str | None) -> str | None:
    if v is None:
        return None
    val = v.strip()
    if not val:
        return None
    cin = val.upper()
    if not re.fullmatch(CIN_REGEX, cin):
        raise ValueError(f"Invalid CIN format: {cin}")
    
    state_code = cin[6:8]
    if state_code not in CIN_STATE_CODES:
        raise ValueError(f"Invalid CIN state code: {state_code}")
        
    return cin


def validate_password_strength(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not any(c.islower() for c in password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one digit")
    if not any(c in "@$!%*?&" for c in password):
        raise ValueError("Password must contain at least one special character (@$!%*?&)")
    return password


def normalize_email(v: str) -> str:
    return v.strip().lower()


# Reusable Normalized Email field type using Pydantic's BeforeValidator
NormalizedEmail = Annotated[EmailStr, BeforeValidator(normalize_email)]


class RegisterStep1Request(BaseModel):
    email: NormalizedEmail
    password: str
    role: Literal["client", "vendor"]

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        return validate_password_strength(v)


class RegisterStep1Response(BaseModel):
    message: str = "OTP sent to your email. Please verify to continue registration."
    email: str
    session_id: str
    otp_dev: str | None = None


class VerifyOTPRequest(BaseModel):
    email: NormalizedEmail
    otp: str = Field(..., min_length=4, max_length=6)
    purpose: str = "registration"
    session_id: str | None = None


class VerifyOTPResponse(BaseModel):
    message: str = "Email verified successfully. Please complete your profile."
    email: str
    temp_token: str | None = None
    session_id: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    role: str | None = None
    token_type: str = "bearer"


class CompleteRegistrationStep1Request(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    gst_number: str = Field(..., min_length=1, max_length=50)

    @field_validator("gst_number")
    @classmethod
    def check_gst_number(cls, v: str) -> str:
        return validate_gst_number(v)
    
    cin: str | None = Field(
        default=None,
        description="21-character Corporate Identification Number (CIN) for Indian companies (Optional)",
        max_length=21,
        examples=["L01110MH2024PTC123456"]
    )

    @field_validator("cin")
    @classmethod
    def check_cin(cls, v: str | None) -> str | None:
        return validate_cin_number(v)

    website_url: str = Field(..., min_length=1, max_length=255)
    company_email: NormalizedEmail
    poc_name: str = Field(..., min_length=1, max_length=255)
    poc_phone: str = Field(..., min_length=1, max_length=20)
    poc_email: NormalizedEmail


class CompleteRegistrationStep2Request(BaseModel):
    domain: str | None = Field(default=None, max_length=255)
    hq_location: str | None = Field(default=None, max_length=255)
    company_size: str | None = Field(default=None, max_length=50)
    certifications: list[str] | None = None
    about_summary: str | None = Field(default=None, max_length=5000)
    founded_year: int | None = None
    linkedin_url: str | None = Field(default=None, max_length=255)
    twitter_url: str | None = Field(default=None, max_length=255)
    instagram_url: str | None = Field(default=None, max_length=255)

    # Vendor-specific
    tech_stack: list[str] | None = None
    has_labour_compliance: bool = False
    pf_registered: bool = False
    esic_registered: bool = False
    gmc_registered: bool = False
    fte_count: int | None = None
    facebook_url: str | None = Field(default=None, max_length=255)
    compliance_checklist: dict | None = None
    declaration_confirmed: bool = False


class CompleteRegistrationResponse(BaseModel):
    message: str = "Registration completed successfully."
    user_id: str
    email: str
    role: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: NormalizedEmail
    password: str


class LoginResponse(BaseModel):
    message: str = "Login successful."
    user_id: str
    email: str
    role: str
    is_verified: bool
    is_profile_complete: bool
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    email: NormalizedEmail


class ForgotPasswordResponse(BaseModel):
    message: str = "If the email exists, a password reset OTP has been sent."
    otp_dev: str | None = None


class ResetPasswordRequest(BaseModel):
    email: NormalizedEmail
    otp: str = Field(..., min_length=4, max_length=6)
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def check_new_password(cls, v: str) -> str:
        return validate_password_strength(v)

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if info.data.get("new_password") != v:
            raise ValueError("Passwords do not match")
        return v


class ResetPasswordResponse(BaseModel):
    message: str = "Password reset successful. Please login with your new password."


class PhoneOTPRequest(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=20, description="Phone number with country code, e.g., +910000000000")


class VerifyPhoneOTPRequest(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=20)
    otp: str = Field(..., min_length=4, max_length=6)
