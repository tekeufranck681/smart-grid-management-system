import logging

import sib_api_v3_sdk
from app.core.config import settings
from app.services.email_templates import (
    build_password_reset_email,
    build_verification_email,
)
from sentry_sdk import metrics
from sib_api_v3_sdk.rest import ApiException

logger = logging.getLogger("email_service")
# Brevo configuration
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key["api-key"] = settings.BREVO_API_KEY

api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
    sib_api_v3_sdk.ApiClient(configuration)
)


class EmailService:
    async def send_verification_email(self, email: str, token: str):
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"

        html_content = build_verification_email(verification_link)

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": email}],
            subject="Verify your email address",
            html_content=html_content,
            sender={
                "email": settings.BREVO_FROM_EMAIL,
                "name": settings.BREVO_FROM_NAME,
            },
        )

        try:
            api_instance.send_transac_email(send_smtp_email)
            metrics.count("email.verification.sent", 1)
        except ApiException as e:
            # Let service layer decide how to handle failures
            logger.error("Failed to send verification email to %s: %s", email, str(e))
            raise RuntimeError(f"Brevo email error: {e}")

    async def send_password_reset_email(self, email: str, token: str):
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

        html_content = build_password_reset_email(reset_link)

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": email}],
            subject="Reset your password",
            html_content=html_content,
            sender={
                "email": settings.BREVO_FROM_EMAIL,
                "name": settings.BREVO_FROM_NAME,
            },
        )

        try:
            api_instance.send_transac_email(send_smtp_email)
            metrics.count("email.password_reset.sent", 1)
        except ApiException as e:
            logger.error("Failed to send password reset email to %s: %s", email, str(e))
            raise RuntimeError(f"Brevo email error: {e}")
