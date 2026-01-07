from app.core.config import settings
from app.database.connection import get_db
from app.dependencies.dependencies import get_current_user
from app.models.auth import RefreshToken
from app.schemas.user import (
    ForgotPasswordRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    UserRequest,
    VerifyTokenRequest,
)
from app.services.auth_service import AuthService
from app.utils.token_generation import create_access_token, create_refresh_token
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from sentry_sdk import metrics
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()


@router.post("/register", status_code=201, description="Register a new user")
async def register_user(user: UserRequest, db: AsyncSession = Depends(get_db)):
    response, status = await auth_service.register(user, db)
    if status != 201:
        raise HTTPException(status_code=status, detail=response.get("error"))

    metrics.count("auth.registration.success", 1)
    return response


@router.post("/verify-email", description="Verify email address")
async def verify_email(
    payload: VerifyTokenRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    token = payload.token
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")

    # Verify token and get user object
    user = await auth_service.verify_email(token, db)
    if not user:
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification token."
        )

    # Generate access and refresh tokens
    access_token = create_access_token(user.id, user.email)
    raw_refresh, refresh_hash, expires_at = create_refresh_token()

    # Store refresh token in DB
    refresh_token_row = RefreshToken(
        user_id=user.id,
        token_hash=refresh_hash,
        expires_at=expires_at,
        revoked=False,
    )
    db.add(refresh_token_row)
    await db.commit()

    # Set tokens in httpOnly cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # change in production (HTTPS)
        samesite="lax",  # allows cross-site requests
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=raw_refresh,
        httponly=True,
        secure=False,  # change in production (HTTPS)
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )

    metrics.count("auth.account_verification.success", 1)

    # Return user info for frontend
    return {
        "status": "success",
        "message": "Email verified successfully.",
        "data": {
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
            "email_verified": user.email_verified,
            "is_active": user.is_active,
        },
    }


@router.post("/resend-verification", description="Resend email verification")
async def resend_verification(
    payload: ResendVerificationRequest, db: AsyncSession = Depends(get_db)
):
    email = payload.email
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    success = await auth_service.resend_verification(email, db)
    if not success:
        raise HTTPException(
            status_code=400, detail="Email address not found or already verified."
        )

    return {"status": "success", "message": "Verification email resent successfully."}


@router.post("/login")
async def login(payload: UserRequest, db: AsyncSession = Depends(get_db)):
    response_data, status = await auth_service.login(payload, db)

    if status != 200:
        raise HTTPException(status_code=status, detail=response_data["detail"])

    response = JSONResponse(content=response_data)

    response.set_cookie(
        key="access_token",
        value=response_data["data"]["access_token"],
        httponly=True,
        secure=False,  # change in production (HTTPS)
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=response_data["data"]["refresh_token"],
        httponly=True,
        secure=False,  # change in production (HTTPS)
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )

    return response


@router.post("/refresh-token")
async def refresh_token(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    access_token = await auth_service.refresh_access_token(refresh_token, db)
    if not access_token:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # change in production (HTTPS)
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    return {
        "status": "success",
        "message": "Access token refreshed",
    }


@router.post("/forgot-password")
async def forgot_password_route(
    payload: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)
):
    response, status = await auth_service.forgot_password(payload.email, db)
    if status != 200:
        raise HTTPException(status_code=status, detail=response["detail"])
    return response


@router.post("/reset-password")
async def reset_password_route(
    payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)
):
    response, status = await auth_service.reset_password(
        payload.token, payload.new_password, db
    )
    if status != 200:
        raise HTTPException(status_code=status, detail=response["detail"])
    return response


@router.post("/logout")
async def logout_route(
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    response_data, status = await auth_service.logout(
        user_id=str(current_user.id), refresh_token=refresh_token, db=db
    )

    if status != 200:
        raise HTTPException(status_code=status, detail=response_data["detail"])

    response = JSONResponse(content=response_data)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return response
