from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import AppException
from app.models.user import User
from app.services.auth_service import AuthService
from app.schemas.auth import (
    RegisterStep1Request, RegisterStep1Response,
    VerifyOTPRequest, VerifyOTPResponse,
    CompleteRegistrationStep1Request, CompleteRegistrationStep2Request,
    CompleteRegistrationResponse,
    LoginRequest, LoginResponse,
    RefreshTokenRequest, RefreshTokenResponse,
    ForgotPasswordRequest, ForgotPasswordResponse,
    ResetPasswordRequest, ResetPasswordResponse,
    PhoneOTPRequest, VerifyPhoneOTPRequest,
    SwitchRoleRequest, SwitchRoleResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/register", response_model=RegisterStep1Response, status_code=status.HTTP_201_CREATED)
async def register_step1(
    request: RegisterStep1Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        result = await auth_service.register_step1(
            email=request.email,
            password=request.password,
            role=request.role,
        )
        return result
    except AppException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/verify-otp", response_model=VerifyOTPResponse)
async def verify_otp(
    request: VerifyOTPRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        result = await auth_service.verify_otp(
            email=request.email,
            otp=request.otp,
            purpose=request.purpose,
            session_id=request.session_id,
        )
        return result
    except AppException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/complete-registration/step1")
async def complete_registration_step1(
    request: CompleteRegistrationStep1Request,
    current_user: Annotated[User, Depends(get_current_user)],
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        result = await auth_service.save_registration_step1(
            user_id=current_user.id,
            **request.model_dump(),
        )
        return result
    except AppException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/complete-registration/step1")
async def get_registration_step1(
    current_user: Annotated[User, Depends(get_current_user)],
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        result = await auth_service.get_registration_step1(user_id=current_user.id)
        return result
    except AppException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/complete-registration", response_model=CompleteRegistrationResponse)
async def complete_registration(
    request: CompleteRegistrationStep2Request,
    current_user: Annotated[User, Depends(get_current_user)],
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        result = await auth_service.complete_registration(
            user_id=current_user.id,
            role=current_user.role.value,
            **request.model_dump(),
        )
        return result
    except AppException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        result = await auth_service.login(
            email=request.email,
            password=request.password,
        )
        return result
    except AppException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        result = await auth_service.refresh_token(request.refresh_token)
        return result
    except AppException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/logout")
async def logout(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        await auth_service.logout(request.refresh_token)
        return {"message": "Logged out successfully"}
    except AppException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        result = await auth_service.forgot_password(request.email)
        return result
    except AppException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    request: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        result = await auth_service.reset_password(
            email=request.email,
            otp=request.otp,
            new_password=request.new_password,
        )
        return result
    except AppException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/switch-role", response_model=SwitchRoleResponse)
async def switch_role(
    request: SwitchRoleRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        result = await auth_service.switch_role(
            email=request.email,
            password=request.password,
            role=request.role,
        )
        return result
    except AppException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/resend-otp")
async def resend_otp(
    email: str,
    purpose: str = "registration",
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        otp = await auth_service.otp_service.send_otp(email, purpose)
        from app.services.email_service import send_otp_email
        send_otp_email(email, otp, purpose)
        return {"message": "OTP resent successfully", "email": email}
    except AppException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/phone-otp")
async def send_phone_otp(
    request: PhoneOTPRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        otp = await auth_service.otp_service.send_phone_otp(request.phone_number)
        return {
            "message": "OTP sent to your phone number successfully",
            "phone_number": request.phone_number,
            "otp_dev": otp
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/verify-phone-otp")
async def verify_phone_otp(
    request: VerifyPhoneOTPRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        is_valid = await auth_service.otp_service.verify_phone_otp(
            phone_number=request.phone_number,
            otp=request.otp,
        )
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")
        return {
            "message": "Phone number verified successfully",
            "phone_number": request.phone_number
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
