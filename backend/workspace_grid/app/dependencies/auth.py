import httpx
from app.core.config import settings
from fastapi import Depends, HTTPException, Request

AUTH_SERVICE_URL = settings.AUTH_SERVICE_URL


async def verify_token(request: Request):
    """
    Verify the access token with the Auth service.
    Returns the full user data dict from Auth service.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Access token missing")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{AUTH_SERVICE_URL}/auth/verify-token",
                cookies={"access_token": token},
                timeout=10,
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        except Exception:
            raise HTTPException(status_code=500, detail="Auth service unreachable")

    data = resp.json().get("data")
    if not data:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return data


async def get_current_user(user_data: dict = Depends(verify_token)):
    """
    Extract current user info from the verified token data.
    Can be extended for role-based checks.
    """
    return {
        "id": user_data["id"],
        "email": user_data["email"],
        "role": user_data["role"],
        "email_verified": user_data["email_verified"],
        "is_active": user_data["is_active"],
    }
