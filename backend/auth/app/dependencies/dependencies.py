from app.database.connection import get_db
from app.models.auth import User
from app.utils.token_generation import decode_access_token
from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Authorization token missing.")

    # Decode token
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload.")

    # Fetch user
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is disabled.")

    return user


async def get_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.email_verified:
        raise HTTPException(status_code=403, detail="Email not verified.")
    return current_user
