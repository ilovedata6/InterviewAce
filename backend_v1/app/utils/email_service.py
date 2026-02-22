import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def send_email(to_email: str, subject: str, body: str):
    smtp_server = getattr(settings, "SMTP_SERVER", None)
    smtp_port = getattr(settings, "SMTP_PORT", 587)
    smtp_username = getattr(settings, "SMTP_USERNAME", None)
    smtp_password = getattr(settings, "SMTP_PASSWORD", None)
    from_email = getattr(settings, "EMAIL_FROM", smtp_username)

    if not all([smtp_server, smtp_port, smtp_username, smtp_password, from_email]):
        raise RuntimeError("Email settings are not properly configured in core/config.py")

    msg = MIMEMultipart()
    msg["From"] = str(from_email)
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(str(smtp_server), smtp_port) as server:
            server.starttls()
            server.login(str(smtp_username), str(smtp_password))
            server.sendmail(str(from_email), to_email, msg.as_string())
    except Exception as e:
        raise RuntimeError(f"Failed to send email: {e}")
