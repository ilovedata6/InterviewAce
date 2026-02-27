"""
Email sending service.

In dev mode (``EMAIL_DEV_MODE=True`` or SMTP not configured), emails are
printed to the console instead of being sent via SMTP.  This prevents
crashes during local development when no mail server is available.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


def send_email(to_email: str, subject: str, body: str) -> None:
    """Send an email — via SMTP in production, or console in dev mode."""
    if settings.EMAIL_DEV_MODE or not settings.is_email_configured:
        # ── Dev-mode console backend ─────────────────────────────────
        logger.info(
            "email_dev_mode",
            to=to_email,
            subject=subject,
        )
        logger.info(
            f"\n{'=' * 60}\n"
            f"  DEV EMAIL (not sent)\n"
            f"{'=' * 60}\n"
            f"  To:      {to_email}\n"
            f"  Subject: {subject}\n"
            f"{'─' * 60}\n"
            f"{body}\n"
            f"{'=' * 60}\n"
        )
        return

    # ── Production SMTP backend ──────────────────────────────────────
    from_email = settings.EMAIL_FROM or settings.SMTP_USERNAME

    msg = MIMEMultipart()
    msg["From"] = str(from_email)
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(str(from_email), to_email, msg.as_string())
        logger.info("email_sent", to=to_email, subject=subject)
    except Exception as e:
        logger.error("email_send_failed", to=to_email, error=str(e))
        raise RuntimeError(f"Failed to send email: {e}") from e
