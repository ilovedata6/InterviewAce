"""
Email Service interface — abstract contract for email delivery.

Concrete implementation: SMTPEmailService (infrastructure/email/).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional


class IEmailService(ABC):
    """Port for outbound email delivery."""

    @abstractmethod
    def send(
        self,
        to_email: str,
        subject: str,
        body: str,
        *,
        html_body: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> None:
        """
        Send an email.

        Args:
            to_email: Recipient address.
            subject: Email subject line.
            body: Plain-text body.
            html_body: Optional HTML body (multipart/alternative).
            cc: Optional list of CC addresses.
            bcc: Optional list of BCC addresses.

        Raises:
            EmailDeliveryError: If sending fails.
        """
        ...

    @abstractmethod
    def send_verification_email(self, to_email: str, token: str, base_url: str) -> None:
        """
        Convenience method to send an email-verification link.

        Args:
            to_email: Recipient address.
            token: The verification token.
            base_url: Application base URL for constructing the link.
        """
        ...

    @abstractmethod
    def send_password_reset_email(self, to_email: str, token: str, base_url: str) -> None:
        """
        Convenience method to send a password-reset link.

        Args:
            to_email: Recipient address.
            token: The reset token.
            base_url: Application base URL for constructing the link.
        """
        ...
