from __future__ import annotations
import enum


class RoleEnum(str, enum.Enum):
    client = "client"
    vendor = "vendor"


class AccountStatusEnum(str, enum.Enum):
    active = "active"
    locked = "locked"
    suspended = "suspended"
    deleted = "deleted"


class RegistrationStepEnum(str, enum.Enum):
    otp_pending = "otp_pending"
    profile_pending = "profile_pending"
    subscription_pending = "subscription_pending"
    completed = "completed"


class OTPPurposeEnum(str, enum.Enum):
    registration = "registration"
    login = "login"
    resend = "resend"
    password_reset = "password_reset"


class SubscriptionPlanEnum(str, enum.Enum):
    free_trial = "free_trial"
    paid = "paid"


class SubscriptionStatusEnum(str, enum.Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"


class DocumentTypeEnum(str, enum.Enum):
    jd = "jd"
    cv = "cv"


class LocationTypeEnum(str, enum.Enum):
    onsite = "onsite"
    hybrid = "hybrid"
    remote = "remote"


class EngagementTypeEnum(str, enum.Enum):
    c2c = "c2c"
    c2h = "c2h"


class AvailabilityEnum(str, enum.Enum):
    immediate = "immediate"
    notice_period = "notice_period"
