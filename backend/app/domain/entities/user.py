"""User domain entity — pure Python, no ORM or framework dependencies."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class UserEntity:
    """Core business representation of a user."""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    full_name: str = ""
    email: str = ""
    hashed_password: str = ""
    is_active: bool = True
    is_email_verified: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Domain behaviour
    # ------------------------------------------------------------------

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False

    def verify_email(self) -> None:
        self.is_email_verified = True

    def is_verified_and_active(self) -> bool:
        return self.is_active and self.is_email_verified
