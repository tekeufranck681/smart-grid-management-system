def build_verification_email(verification_link: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8" />
        <title>Email Verification</title>
    </head>
    <body style="font-family: Arial, sans-serif; background:#f6f9fc; padding:40px;">
        <div style="max-width:600px;margin:auto;background:#fff;padding:30px;border-radius:8px;">
            <h2 style="color:#0066cc;">Verify your email</h2>
            <p>
                Thank you for registering. Please confirm your email address by clicking the button below:
            </p>

            <a href="{verification_link}"
               style="
                 display:inline-block;
                 margin-top:20px;
                 padding:12px 24px;
                 background:#0066cc;
                 color:#ffffff;
                 text-decoration:none;
                 border-radius:5px;
               ">
                Verify Email
            </a>

            <p style="margin-top:30px;font-size:0.9em;color:#666;">
                This link will expire in 24 hours.
                If you did not create this account, please ignore this email.
            </p>
        </div>
    </body>
    </html>
    """


def build_password_reset_email(reset_link: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8" />
        <title>Password Reset</title>
    </head>
    <body style="font-family: Arial, sans-serif; background:#f6f9fc; padding:40px;">
        <div style="max-width:600px;margin:auto;background:#fff;padding:30px;border-radius:8px;">
            <h2 style="color:#cc0000;">Reset your password</h2>

            <p>
                We received a request to reset your password.
                Click the button below to choose a new one.
            </p>

            <a href="{reset_link}"
               style="
                 display:inline-block;
                 margin-top:20px;
                 padding:12px 24px;
                 background:#cc0000;
                 color:#ffffff;
                 text-decoration:none;
                 border-radius:5px;
               ">
                Reset Password
            </a>

            <p style="margin-top:30px;font-size:0.9em;color:#666;">
                This link will expire in 1 hour.
                If you did not request a password reset, please ignore this email.
            </p>
        </div>
    </body>
    </html>
    """
