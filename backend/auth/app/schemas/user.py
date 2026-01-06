from pydantic import BaseModel, EmailStr, Field


class UserRequest(BaseModel):
    email: EmailStr = Field(..., description="The email address of the new user")
    password: str = Field(..., description="The desired password for the new user")


class VerifyTokenRequest(BaseModel):
    token: str = Field(..., description="The access token to be verified")


class ResendVerificationRequest(BaseModel):
    email: EmailStr = Field(
        ..., description="The email address of the user to resend verification"
    )


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(
        ..., description="The email address of the user requesting a password reset"
    )


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="The password reset token")
    new_password: str = Field(..., description="The new password for the user")
