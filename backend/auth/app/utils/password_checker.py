import re

from fastapi import HTTPException


def verify_password_strength(password: str):
    if len(password) < 8:
        raise HTTPException(
            status_code=400, detail="Password must be at least 8 characters"
        )

    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one uppercase letter",
        )

    if not re.search(r"[a-z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one lowercase letter",
        )

    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=400, detail="Password must contain at least one number"
        )

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one special character",
        )

    # optional: check for common passwords
    common_passwords = ["password", "123456", "qwerty", "welcome", "admin", "letmein"]
    if password.lower() in common_passwords:
        raise HTTPException(status_code=400, detail="Password is too common")

    return True
