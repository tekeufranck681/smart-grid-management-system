import uuid
from datetime import datetime, timedelta

from app.cache.cache_service import CacheService
from app.core.config import settings
from app.models.auth import (
    EmailVerificationToken,
    PasswordResetToken,
    RefreshToken,
    User,
)
from app.schemas.user import UserRequest
from app.services.email_service import EmailService
from app.utils.password_checker import verify_password_strength
from app.utils.security import hash_password, hash_token, verify_password
from app.utils.token_generation import create_access_token, create_refresh_token
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class AuthService:
    def __init__(self):
        self.cache = CacheService(namespace="email_verification")
        self.password_reset_cache = CacheService(namespace="password_reset")
        self.email_service = EmailService()

    async def register(self, user_data: UserRequest, db: AsyncSession):
        # Validate password strength
        if not verify_password_strength(user_data.password):
            return {"error": "Password does not meet strength requirements"}, 400

        # Check if email exists
        stmt = select(User).where(User.email == user_data.email)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            return {"error": "Email already exists"}, 400

        # Create user
        new_user = User(
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            role="user",
            email_verified=False,
            is_active=True,
        )
        db.add(new_user)
        await db.flush()  # get user.id without commit

        # Generate verification token
        raw_token = str(uuid.uuid4())
        token_hash = hash_token(raw_token)

        expires_at = datetime.utcnow() + timedelta(
            hours=settings.EMAIL_VERIFICATION_TTL_HOURS
        )

        email_token = EmailVerificationToken(
            user_id=new_user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            used=False,
        )

        db.add(email_token)
        await db.commit()

        # Cache token hash
        await self.cache.set(
            token_hash,
            {"user_id": str(new_user.id)},
            ttl=settings.EMAIL_VERIFICATION_TTL_HOURS * 3600,
        )

        # Send verification email (raw token only)
        await self.email_service.send_verification_email(new_user.email, raw_token)

        return {
            "message": "User registered successfully. Please verify your email to activate your account."
        }, 201

    async def verify_email(self, token: str, db: AsyncSession):
        token_hash = hash_token(token)

        stmt = select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == token_hash,
            not EmailVerificationToken.used,
        )
        result = await db.execute(stmt)
        token_row = result.scalar_one_or_none()

        if not token_row or token_row.expires_at < datetime.utcnow():
            return None  # failure

        user = await db.get(User, token_row.user_id)
        if not user or user.email_verified:
            return None  # already verified

        # Mark token used and verify user
        token_row.used = True
        user.email_verified = True

        await db.commit()
        await self.cache.delete(token_hash)

        return user  # return the user object

    async def resend_verification(self, email: str, db: AsyncSession):
        # Fetch user
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or user.email_verified:
            # Either user doesn't exist or already verified
            return False

        # Invalidate all previous unused tokens
        await db.execute(
            update(EmailVerificationToken)
            .where(
                EmailVerificationToken.user_id == user.id,
                not EmailVerificationToken.used,
            )
            .values(used=True)
        )

        # Generate new token
        raw_token = str(uuid.uuid4())
        token_hash = hash_token(raw_token)
        expires_at = datetime.utcnow() + timedelta(
            hours=settings.EMAIL_VERIFICATION_TTL_HOURS
        )

        token_row = EmailVerificationToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            used=False,
        )

        db.add(token_row)
        await db.commit()

        # Cache new token
        await self.cache.set(
            token_hash,
            {"user_id": str(user.id)},
            ttl=settings.EMAIL_VERIFICATION_TTL_HOURS * 3600,
        )

        # Send verification email
        await self.email_service.send_verification_email(user.email, raw_token)

        return True

    async def login(self, user_data: UserRequest, db: AsyncSession):
        # Fetch user
        stmt = select(User).where(User.email == user_data.email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        # Verify password first
        if not user or not verify_password(user_data.password, user.password_hash):
            return {"detail": "Invalid email or password."}, 401

        # Check email verified
        if not user.email_verified:
            return {
                "detail": "Email address not verified. Please verify your email before logging in."
            }, 403

        # Generate access token
        access_token = create_access_token(user.id, user.email)
        raw_refresh, refresh_hash, expires_at = create_refresh_token()

        # Store refresh token
        refresh_token_row = RefreshToken(
            user_id=user.id,
            token_hash=refresh_hash,
            expires_at=expires_at,
            revoked=False,
        )
        db.add(refresh_token_row)
        await db.commit()

        return {
            "status": "success",
            "data": {
                "id": str(user.id),
                "email": user.email,
                "role": user.role,
                "email_verified": user.email_verified,
                "is_active": user.is_active,
                "access_token": access_token,
                "refresh_token": raw_refresh,
            },
            "message": "Login successful.",
        }, 200

    async def refresh_access_token(self, refresh_token: str, db: AsyncSession):
        token_hash = hash_token(refresh_token)

        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash, not RefreshToken.revoked
        )
        result = await db.execute(stmt)
        token_row = result.scalar_one_or_none()

        if not token_row or token_row.expires_at < datetime.utcnow():
            return None

        user = await db.get(User, token_row.user_id)
        if not user or not user.is_active:
            return None

        # Only issue new access token
        access_token = create_access_token(user.id, user.email)

        return access_token

    async def forgot_password(self, email: str, db: AsyncSession):
        # Find user
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return {"detail": "Email address not found"}, 400

        # Generate password reset token
        raw_token = str(uuid.uuid4())
        token_hash = hash_token(raw_token)
        expires_at = datetime.utcnow() + timedelta(
            hours=settings.PASSWORD_RESET_TTL_HOURS
        )

        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            used=False,
        )
        db.add(reset_token)
        await db.commit()

        # Cache token hash
        await self.password_reset_cache.set(
            token_hash,
            {"user_id": str(user.id)},
            ttl=settings.PASSWORD_RESET_TTL_HOURS * 3600,
        )
        # Send password reset email
        await self.email_service.send_password_reset_email(user.email, raw_token)

        return {
            "status": "success",
            "message": "Password reset link sent to your email.",
        }, 200

    async def reset_password(self, token: str, new_password: str, db: AsyncSession):
        # Validate new password strength
        if not verify_password_strength(new_password):
            return {"detail": "Password does not meet strength requirements."}, 400

        token_hash = hash_token(token)
        await self.password_reset_cache.get(token_hash)

        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash
        )
        result = await db.execute(stmt)
        reset_token = result.scalar_one_or_none()

        if not reset_token or reset_token.used or reset_token.revoked:
            return {"detail": "Invalid or expired password reset token."}, 400

        if reset_token.expires_at < datetime.utcnow():
            return {"detail": "Invalid or expired password reset token."}, 400

        # Find user
        stmt_user = select(User).where(User.id == reset_token.user_id)
        result_user = await db.execute(stmt_user)
        user = result_user.scalar_one_or_none()

        if not user or not user.is_active:
            return {"detail": "User not found or inactive."}, 400

        # Update password
        user.password_hash = hash_password(new_password)
        db.add(user)

        # Mark token used
        reset_token.used = True
        db.add(reset_token)

        # Revoke all refresh tokens
        stmt_tokens = select(RefreshToken).where(RefreshToken.user_id == user.id)
        result_tokens = await db.execute(stmt_tokens)
        for rt in result_tokens.scalars().all():
            rt.revoked = True
            db.add(rt)

        await db.commit()

        await self.password_reset_cache.delete(token_hash)

        return {
            "status": "success",
            "message": "Password has been reset successfully.",
        }, 200

    async def logout(self, user_id: str, refresh_token: str, db: AsyncSession):
        token_hash = hash_token(refresh_token)

        # Fetch refresh token
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.user_id == user_id,
            not RefreshToken.revoked,
        )
        result = await db.execute(stmt)
        stored_token = result.scalar_one_or_none()

        if not stored_token:
            return {"detail": "Invalid or already revoked refresh token."}, 401

        # Revoke token
        stored_token.revoked = True
        db.add(stored_token)
        await db.commit()

        return {"status": "success", "message": "Logout successful."}, 200
