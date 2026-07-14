from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete

from app.config import settings
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    hash_token, verify_token_hash,
)
from app.core.otp import generate_otp
from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError, ValidationError
from app.models.user import User
from app.models.enums import RoleEnum, AccountStatusEnum, RegistrationStepEnum, OTPPurposeEnum
from app.models.otp_verification import OTPVerification
from app.models.client_profile import ClientProfile
from app.models.vendor_profile import VendorProfile
from app.models.refresh_token import RefreshToken
from app.repositories.user_repository import UserRepository
from app.services.otp_service import OTPService
from app.services.email_service import send_otp_email, send_password_reset_email
from app.tasks.notification_tasks import send_sms


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.otp_service = OTPService(db)

    async def register_step1(self, email: str, password: str, role: str) -> dict[str, Any]:
        email = email.strip().lower()
        existing = await self.user_repo.get_by_email(email)
        if existing:
            # Check existing password for security
            if not verify_password(password, existing.password_hash):
                raise AuthenticationError("An account already exists with this email, but the password provided is incorrect.")
            
            # Check existing role
            if existing.role.value == role:
                if existing.registration_step == RegistrationStepEnum.completed:
                    raise ConflictError("An account already exists with this email.")
                else:
                    # Continue onboarding: resend OTP and generate registration session
                    session_id = str(uuid.uuid4())
                    session_data = {
                        "email": email,
                        "password_hash": existing.password_hash,
                        "role": role,
                        "email_verified": False,
                        "phone": None,
                        "phone_verified": False
                    }
                    await self.otp_service.redis.setex(
                        f"reg_session:{session_id}",
                        3600,
                        json.dumps(session_data)
                    )
                    otp_code = await self.otp_service.send_otp(email, purpose="registration")
                    send_otp_email(email, otp_code, purpose="registration")
                    
                    res = {
                        "email": email,
                        "session_id": session_id,
                        "message": "Continuing registration. OTP sent to your email."
                    }
                    if settings.ENVIRONMENT == "development":
                        res["otp_dev"] = otp_code
                    return res
            else:
                # Role is different
                raise ConflictError(json.dumps({
                    "error_code": "ROLE_MISMATCH",
                    "message": f"This email is already registered as {existing.role.value.capitalize()}. Do you want to switch to {role.capitalize()}?",
                    "existing_role": existing.role.value,
                    "target_role": role
                }))

        # Generate unique registration session ID
        session_id = str(uuid.uuid4())
        password_hash = hash_password(password)

        # Store user staging data temporarily in Redis (TTL: 1 hour)
        session_data = {
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "email_verified": False,
            "phone": None,
            "phone_verified": False
        }
        await self.otp_service.redis.setex(
            f"reg_session:{session_id}",
            3600,
            json.dumps(session_data)
        )

        # Generate and save Email OTP in PostgreSQL
        otp_code = await self.otp_service.send_otp(email, purpose="registration")

        # Send OTP email
        send_otp_email(email, otp_code, purpose="registration")

        res = {
            "email": email,
            "session_id": session_id,
            "message": "OTP sent to your email. Please verify to continue registration."
        }
        if settings.ENVIRONMENT == "development":
            res["otp_dev"] = otp_code
        return res

    async def verify_otp(self, email: str, otp: str, purpose: str = "registration", session_id: str | None = None) -> dict[str, Any]:
        email = email.strip().lower()

        # If purpose is password_reset, verify via standard Redis OTP service
        if purpose == "password_reset":
            user = await self.user_repo.get_by_email(email)
            if not user:
                raise NotFoundError("User not found")
            is_valid = await self.otp_service.verify_otp(email, otp, purpose)
            if not is_valid:
                raise ValidationError("Invalid or expired OTP")
            
            temp_token = create_access_token(
                data={"sub": user.id, "email": user.email, "type": purpose},
                expires_delta=timedelta(minutes=30)
            )
            return {
                "email": email,
                "message": "Email verified successfully",
                "temp_token": temp_token,
            }

        # Otherwise, registration staging flow
        if not session_id:
            raise ValidationError("session_id is required for registration verification")

        session_key = f"reg_session:{session_id}"
        session_raw = await self.otp_service.redis.get(session_key)
        if not session_raw:
            raise ValidationError("Registration session expired or invalid. Please request a new OTP.")

        session_data = json.loads(session_raw)
        if session_data["email"] != email:
            raise ValidationError("Email mismatch for this registration session")

        # Verify OTP code and attempts counter from PostgreSQL
        is_valid = await self.otp_service.verify_otp(email, otp, purpose="registration")
        if not is_valid:
            raise ValidationError("Invalid or expired OTP")

        # 1. Create and Save the User in PostgreSQL immediately
        user = User(
            email=email,
            password_hash=session_data["password_hash"],
            role=RoleEnum(session_data["role"]),
            is_verified=True,
            account_status=AccountStatusEnum.active,
            registration_step=RegistrationStepEnum.profile_pending
        )
        self.db.add(user)
        await self.db.flush()

        # Delete Redis registration session and database OTP keys
        await self.otp_service.redis.delete(session_key)
        await self.otp_service.delete_otp(email, purpose="registration")

        # Generate tokens
        access_token = create_access_token(data={"sub": user.id, "role": user.role.value})
        refresh_token_raw = create_refresh_token(data={"sub": user.id})

        refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token_raw),
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(refresh_token)
        await self.db.commit()

        return {
            "email": email,
            "message": "Email verified successfully. Please complete your profile.",
            "session_id": session_id,
            "access_token": access_token,
            "refresh_token": refresh_token_raw,
            "role": user.role.value,
        }

    async def save_registration_step1(self, user_id: str, company_name: str, gst_number: str, cin: str | None, website_url: str, company_email: str, poc_name: str, poc_phone: str, poc_email: str) -> dict[str, Any]:
        # Enforce phone verification: Check if phone_verified:<phone> key is set in Redis to "true"
        phone_verified_key = f"phone_verified:{poc_phone}"
        verified_flag = await self.otp_service.redis.get(phone_verified_key)
        if not verified_flag:
            raise ValidationError("Phone number must be verified first")

        # Save initial details in Redis under reg_profile:{user_id} (TTL: 1 hour)
        profile_data = {
            "company_name": company_name,
            "gst_number": gst_number,
            "cin": cin,
            "website_url": website_url,
            "company_email": company_email,
            "poc_name": poc_name,
            "poc_phone": poc_phone,
            "poc_email": poc_email
        }
        await self.otp_service.redis.setex(
            f"reg_profile:{user_id}",
            3600,
            json.dumps(profile_data)
        )
        return {"message": "Initial profile details saved temporarily in Redis."}

    async def get_registration_step1(self, user_id: str) -> dict[str, Any]:
        profile_key = f"reg_profile:{user_id}"
        profile_raw = await self.otp_service.redis.get(profile_key)
        if not profile_raw:
            raise NotFoundError("Staging profile details not found or expired.")
        return json.loads(profile_raw)

    async def complete_registration(self, user_id: str, role: str, **step2_data: Any) -> dict[str, Any]:
        profile_key = f"reg_profile:{user_id}"
        profile_raw = await self.otp_service.redis.get(profile_key)
        if not profile_raw:
            raise ValidationError("Initial registration details not found. Please complete page 1 first.")

        initial_data = json.loads(profile_raw)

        # Merge initial details and remaining details
        company_name = initial_data["company_name"]
        gst_number = initial_data["gst_number"]
        cin = initial_data["cin"]
        website_url = initial_data["website_url"]
        company_email = initial_data["company_email"]
        poc_name = initial_data["poc_name"]
        poc_phone = initial_data["poc_phone"]
        poc_email = initial_data["poc_email"]

        # Fetch the user
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        # Extract domain if website url is provided
        domain = step2_data.get("domain")
        if website_url and not domain:
            from app.utils.company import extract_domain
            domain = extract_domain(website_url)

        hq_location = step2_data.get("hq_location")
        founded_year = step2_data.get("founded_year")
        if company_name and (not hq_location or not founded_year):
            from app.utils.company import fetch_wikidata_company_data
            external_data = await fetch_wikidata_company_data(company_name)
            if not hq_location:
                hq_location = external_data.get("hq_location")
            if not founded_year:
                founded_year = external_data.get("founded_year")

        # Create corresponding Profile
        if role == "client":
            profile = ClientProfile(
                user_id=user.id,
                company_name=company_name,
                gst_number=gst_number,
                cin=cin,
                website_url=website_url,
                company_email=company_email,
                poc_name=poc_name,
                poc_phone=poc_phone,
                poc_email=poc_email,
                domain=domain,
                hq_location=hq_location,
                company_size=step2_data.get("company_size"),
                certifications=step2_data.get("certifications"),
                about_summary=step2_data.get("about_summary"),
                founded_year=founded_year,
                linkedin_url=step2_data.get("linkedin_url"),
                twitter_url=step2_data.get("twitter_url"),
                instagram_url=step2_data.get("instagram_url"),
            )
            self.db.add(profile)
        elif role == "vendor":
            profile = VendorProfile(
                user_id=user.id,
                company_name=company_name,
                gst_number=gst_number,
                cin=cin,
                website_url=website_url,
                company_email=company_email,
                poc_name=poc_name,
                poc_phone=poc_phone,
                poc_email=poc_email,
                tech_stack=step2_data.get("tech_stack"),
                hq_location=hq_location,
                company_size=step2_data.get("company_size"),
                certifications=step2_data.get("certifications"),
                about_summary=step2_data.get("about_summary"),
                founded_year=founded_year,
                has_labour_compliance=step2_data.get("has_labour_compliance", False),
                pf_registered=step2_data.get("pf_registered", False),
                esic_registered=step2_data.get("esic_registered", False),
                gmc_registered=step2_data.get("gmc_registered", False),
                fte_count=step2_data.get("fte_count"),
                vendor_model=step2_data.get("vendor_model"),
                compliance_checklist=step2_data.get("compliance_checklist"),
                declaration_confirmed=step2_data.get("declaration_confirmed", False),
                linkedin_url=step2_data.get("linkedin_url"),
                twitter_url=step2_data.get("twitter_url"),
                instagram_url=step2_data.get("instagram_url"),
                facebook_url=step2_data.get("facebook_url"),
            )
            self.db.add(profile)
        else:
            raise ValidationError("Invalid role")

        # Update user's registration step
        user.registration_step = RegistrationStepEnum.subscription_pending
        await self.db.flush()

        # Delete staging keys
        await self.otp_service.redis.delete(profile_key)
        await self.otp_service.redis.delete(f"phone_verified:{poc_phone}")

        # Generate tokens
        access_token = create_access_token(data={"sub": user.id, "role": user.role.value})
        refresh_token_raw = create_refresh_token(data={"sub": user.id})

        refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token_raw),
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(refresh_token)
        await self.db.commit()

        return {
            "message": "Registration completed successfully.",
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value,
            "access_token": access_token,
            "refresh_token": refresh_token_raw,
        }

    async def login(self, email: str, password: str) -> dict[str, Any]:
        email = email.strip().lower()
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise AuthenticationError("Invalid email or password")

        # Enforce account status locks/suspensions
        if user.account_status == AccountStatusEnum.locked:
            raise AuthenticationError("Account is locked")
        elif user.account_status == AccountStatusEnum.suspended:
            raise AuthenticationError("Account is suspended")
        elif user.account_status == AccountStatusEnum.deleted:
            raise AuthenticationError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password")

        # Check step status to decide redirects
        is_profile_complete = user.registration_step != RegistrationStepEnum.otp_pending and user.registration_step != RegistrationStepEnum.profile_pending

        # Standard logins for registered users will have is_verified=True and step beyond otp_pending
        access_token = create_access_token(data={"sub": user.id, "role": user.role.value})
        refresh_token_raw = create_refresh_token(data={"sub": user.id})

        refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token_raw),
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(refresh_token)
        await self.db.commit()

        return {
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value,
            "is_verified": user.is_verified,
            "is_profile_complete": is_profile_complete,
            "access_token": access_token,
            "refresh_token": refresh_token_raw,
        }

    async def refresh_token(self, refresh_token_raw: str) -> dict[str, Any]:
        from app.core.security import decode_token

        payload = decode_token(refresh_token_raw)
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token")

        user_id = payload.get("sub")
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise AuthenticationError("User not found")

        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,
            )
        )
        tokens = result.scalars().all()

        valid_token = None
        for token in tokens:
            if verify_token_hash(refresh_token_raw, token.token_hash):
                valid_token = token
                break

        if not valid_token:
            raise AuthenticationError("Invalid or revoked refresh token")

        if valid_token.expires_at < datetime.utcnow():
            raise AuthenticationError("Refresh token expired")

        valid_token.is_revoked = True
        valid_token.revoked_at = datetime.utcnow()

        new_access_token = create_access_token(data={"sub": user.id, "role": user.role.value})
        new_refresh_token_raw = create_refresh_token(data={"sub": user.id})

        new_refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(new_refresh_token_raw),
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            replaced_by_token_id=None,
        )
        self.db.add(new_refresh_token)
        await self.db.flush()

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token_raw,
        }

    async def logout(self, refresh_token_raw: str) -> None:
        result = await self.db.execute(select(RefreshToken).where(RefreshToken.is_revoked == False))
        tokens = result.scalars().all()

        for token in tokens:
            if verify_token_hash(refresh_token_raw, token.token_hash):
                token.is_revoked = True
                token.revoked_at = datetime.utcnow()
                await self.db.flush()
                return

        raise AuthenticationError("Invalid refresh token")

    async def forgot_password(self, email: str) -> dict[str, Any]:
        import secrets
        from datetime import timedelta
        from app.models.user import get_ist_now
        from app.models.password_reset_token import PasswordResetToken

        user = await self.user_repo.get_by_email(email)
        if not user:
            return {"message": "If the email exists, a password reset OTP has been sent."}

        otp = await self.otp_service.send_otp(email, purpose="password_reset")
        send_password_reset_email(email, otp)

        # Generate unique token for reset
        reset_token = secrets.token_urlsafe(32)
        token_hash = hash_token(reset_token)

        # Save password reset record in DB
        expires_at = get_ist_now() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        password_reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            otp_code=otp,
            is_used=False,
            expires_at=expires_at,
        )
        self.db.add(password_reset_token)
        await self.db.flush()

        res = {"message": "If the email exists, a password reset OTP has been sent."}
        if settings.ENVIRONMENT == "development":
            res["otp_dev"] = otp
            res["reset_token_dev"] = reset_token
        return res

    async def reset_password(self, email: str, otp: str, new_password: str) -> dict[str, Any]:
        is_valid = await self.otp_service.verify_otp(email, otp, purpose="password_reset")
        if not is_valid:
            raise ValidationError("Invalid or expired OTP")

        user = await self.user_repo.get_by_email(email)
        if not user:
            raise NotFoundError("User not found")

        # Mark token as used in DB
        from app.models.user import get_ist_now
        from app.models.password_reset_token import PasswordResetToken
        from sqlalchemy import and_

        result = await self.db.execute(
            select(PasswordResetToken).where(
                and_(
                    PasswordResetToken.user_id == user.id,
                    PasswordResetToken.otp_code == otp,
                    PasswordResetToken.is_used == False
                )
            ).order_by(PasswordResetToken.created_at.desc())
        )
        pw_reset_token = result.scalar_one_or_none()
        if pw_reset_token:
            pw_reset_token.is_used = True
            pw_reset_token.used_at = get_ist_now()

        user.password_hash = hash_password(new_password)

        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user.id,
                RefreshToken.is_revoked == False,
            )
        )
        tokens = result.scalars().all()
        for token in tokens:
            token.is_revoked = True
            token.revoked_at = datetime.utcnow()

        await self.user_repo.update(user)

        return {"message": "Password reset successful"}

    async def switch_role(self, email: str, password: str, role: str) -> dict[str, Any]:
        email = email.strip().lower()
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise NotFoundError("User not found.")

        # Verify password
        if not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password.")

        # Verify role is different
        if user.role.value == role:
            raise ValidationError(f"User is already registered with role {role}.")

        # Switch role in DB
        user.role = RoleEnum(role)
        user.registration_step = RegistrationStepEnum.profile_pending
        await self.user_repo.update(user)

        # Delete old profile to prevent mismatching data
        if role == "vendor":
            from app.models.client_profile import ClientProfile
            await self.db.execute(delete(ClientProfile).where(ClientProfile.user_id == user.id))
        else:
            from app.models.vendor_profile import VendorProfile
            await self.db.execute(delete(VendorProfile).where(VendorProfile.user_id == user.id))

        await self.db.flush()

        # Generate new auth tokens for ongoing onboarding session
        access_token = create_access_token(data={"sub": user.id, "role": user.role.value})
        refresh_token_raw = create_refresh_token(data={"sub": user.id})

        # Store new refresh token
        from app.models.refresh_token import RefreshToken
        token_hash = hash_token(refresh_token_raw)
        from app.models.user import get_ist_now
        db_refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            is_revoked=False,
            expires_at=get_ist_now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        self.db.add(db_refresh_token)
        await self.db.flush()

        return {
            "message": "Role switched successfully. Please complete your profile onboarding.",
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value,
            "access_token": access_token,
            "refresh_token": refresh_token_raw,
            "token_type": "bearer"
        }
