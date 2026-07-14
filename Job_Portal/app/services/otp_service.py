from __future__ import annotations

import random
import string
import uuid
from datetime import timedelta
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete

from app.config import settings
from app.core.otp import generate_otp
from app.core.security import hash_password, verify_password
from app.tasks.notification_tasks import send_sms


class OTPService:
    def __init__(self, db: AsyncSession | None = None):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.db = db

    async def _get_rate_limit_key(self, email: str, purpose: str) -> str:
        return f"otp_rate_limit:{purpose}:{email}"

    async def _get_otp_key(self, email: str, purpose: str) -> str:
        return f"otp:{purpose}:{email}"

    async def check_rate_limit(self, email: str, purpose: str) -> bool:
        key = await self._get_rate_limit_key(email, purpose)
        count = await self.redis.get(key)
        if count is None:
            return True
        return int(count) < settings.OTP_RATE_LIMIT_PER_MINUTE

    async def increment_rate_limit(self, email: str, purpose: str) -> None:
        key = await self._get_rate_limit_key(email, purpose)
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)
        await pipe.execute()

    async def send_otp(self, email: str, purpose: str = "registration") -> str:
        if not await self.check_rate_limit(email, purpose):
            raise Exception("Too many OTP requests. Please try again after a minute.")

        otp = generate_otp(length=4)
        otp_hash = hash_password(otp)

        if self.db:
            from app.models.enums import OTPPurposeEnum
            from app.models.otp_verification import OTPVerification
            from app.models.user import User, get_ist_now
            
            # Delete any existing OTPs for the same email and purpose
            await self.db.execute(
                delete(OTPVerification).where(
                    and_(
                        OTPVerification.email == email,
                        OTPVerification.purpose == OTPPurposeEnum(purpose)
                    )
                )
            )
            
            # Retrieve user if exists (e.g. for password resets)
            result = await self.db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            user_id = user.id if user else None
            
            expires_at = get_ist_now() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
            
            otp_verification = OTPVerification(
                user_id=user_id,
                email=email,
                otp_hash=otp_hash,
                purpose=OTPPurposeEnum(purpose),
                is_verified=False,
                expires_at=expires_at,
                attempts=0,
                max_attempts=settings.OTP_MAX_ATTEMPTS
            )
            self.db.add(otp_verification)
            await self.db.flush()

        # Store raw OTP in Redis for development testing
        if settings.ENVIRONMENT == "development":
            await self.redis.setex(f"test_otp:{purpose}:{email}", 600, otp)
            
        await self.increment_rate_limit(email, purpose)

        return otp

    async def verify_otp(self, email: str, otp: str, purpose: str = "registration") -> bool:
        if self.db:
            from app.models.enums import OTPPurposeEnum
            from app.models.otp_verification import OTPVerification
            from app.models.user import get_ist_now
            
            stmt = select(OTPVerification).where(
                and_(
                    OTPVerification.email == email,
                    OTPVerification.purpose == OTPPurposeEnum(purpose),
                    OTPVerification.is_verified == False
                )
            ).order_by(OTPVerification.created_at.desc())
            
            result = await self.db.execute(stmt)
            otp_verification = result.scalar_one_or_none()
            
            if otp_verification is None:
                return False
                
            if otp_verification.expires_at < get_ist_now():
                return False
                
            if otp_verification.attempts >= otp_verification.max_attempts:
                return False
                
            is_valid = verify_password(otp, otp_verification.otp_hash)
            if is_valid:
                otp_verification.is_verified = True
                await self.db.flush()
                return True
            else:
                otp_verification.attempts += 1
                await self.db.flush()
                return False
        return False

    async def delete_otp(self, email: str, purpose: str = "registration") -> None:
        if self.db:
            from app.models.enums import OTPPurposeEnum
            from app.models.otp_verification import OTPVerification
            
            await self.db.execute(
                delete(OTPVerification).where(
                    and_(
                        OTPVerification.email == email,
                        OTPVerification.purpose == OTPPurposeEnum(purpose)
                    )
                )
            )
            await self.db.flush()

    async def send_phone_otp(self, phone_number: str) -> str:
        # Simple rate limit key for phone number
        rate_key = f"otp_rate_limit:phone:{phone_number}"
        count = await self.redis.get(rate_key)
        if count and int(count) >= settings.OTP_RATE_LIMIT_PER_MINUTE:
            raise Exception("Too many OTP requests. Please try again after a minute.")

        otp = generate_otp(length=4)
        otp_hash = hash_password(otp)

        # Store OTP in Redis for 10 minutes
        await self.redis.setex(f"phone_otp:{phone_number}", 600, otp_hash)

        # Increment rate limit
        pipe = self.redis.pipeline()
        pipe.incr(rate_key)
        pipe.expire(rate_key, 60)
        await pipe.execute()

        # Send SMS via Celery task
        send_sms.delay(phone_number, f"Your Job Portal OTP code is: {otp}. It will expire in 10 minutes.")

        return otp

    async def verify_phone_otp(self, phone_number: str, otp: str) -> bool:
        key = f"phone_otp:{phone_number}"
        stored_hash = await self.redis.get(key)

        if stored_hash is None:
            return False

        is_valid = verify_password(otp, stored_hash)
        if is_valid:
            # Delete the verification OTP
            await self.redis.delete(key)
            # Store verified state for 15 minutes (900 seconds)
            await self.redis.setex(f"phone_verified:{phone_number}", 900, "true")

        return is_valid

    async def save_pending_registration(self, email: str, password_hash: str, role: str) -> None:
        key = f"pending_registration:{email}"
        import json
        data = json.dumps({"password_hash": password_hash, "role": role})
        await self.redis.setex(key, settings.OTP_EXPIRE_MINUTES * 60, data)

    async def get_pending_registration(self, email: str) -> dict[str, str] | None:
        key = f"pending_registration:{email}"
        data = await self.redis.get(key)
        if not data:
            return None
        import json
        return json.loads(data)

    async def delete_pending_registration(self, email: str) -> None:
        key = f"pending_registration:{email}"
        await self.redis.delete(key)

    async def close(self) -> None:
        await self.redis.close()
