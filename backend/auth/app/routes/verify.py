from app.database.connection import get_db
from app.models.auth import User
from app.utils.token_generation import decode_access_token
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Token Verification"])


@router.post("/verify-token", description="Verify access token and return user context")
async def verify_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Access token missing")

    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return {
        "status": "success",
        "data": {
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
            "email_verified": user.email_verified,
            "is_active": user.is_active,
        },
    }
