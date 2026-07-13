from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    id: str
    email: str
    role: str
    is_verified: bool
    company_name: str | None = None
    account_status: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
