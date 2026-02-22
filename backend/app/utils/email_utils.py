from app.core.config import settings
from app.utils.email_service import send_email

def send_verification_email(to_email: str, token: str):
    verify_url = f"https://frontend-domain.com/verify-email?token={token}"
    subject = "Verify Your Interview Ace Email"
    body = (
        f"Hi,\n\n"
        "Please verify your email address by clicking the link below (valid for 30 minutes):\n"
        f"{verify_url}\n\n"
        "If you did not register, you can ignore this email.\n"
    )
    send_email(to_email=to_email, subject=subject, body=body)
