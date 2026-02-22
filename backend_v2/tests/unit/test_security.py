"""
Unit tests for app.core.security — password hashing, JWT tokens, CSRF,
email verification tokens, and password validation.

These tests are pure unit tests with NO database interaction.
"""

from __future__ import annotations

import os
from datetime import timedelta

import pytest
from jose import jwt

# Ensure test env vars before importing security module
os.environ.setdefault("SECRET_KEY", "a" * 64)
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")

from app.core.security import (
    validate_password_complexity,
    verify_password,
    get_password_hash,
    create_token,
    create_tokens,
    generate_csrf_token,
    verify_csrf_token,
    generate_email_verification_token,
    verify_email_verification_token,
    AuthenticationException,
    SecurityException,
)
from app.core.config import settings


# ---------------------------------------------------------------------------
# Password complexity validation
# ---------------------------------------------------------------------------

class TestPasswordComplexity:
    def test_valid_password(self):
        assert validate_password_complexity("Test@1234") is True

    def test_missing_uppercase(self):
        assert validate_password_complexity("test@1234") is False

    def test_missing_lowercase(self):
        assert validate_password_complexity("TEST@1234") is False

    def test_missing_digit(self):
        assert validate_password_complexity("Test@abcd") is False

    def test_missing_special_char(self):
        assert validate_password_complexity("Test12345") is False

    def test_too_short(self):
        assert validate_password_complexity("Te@1") is False

    def test_empty_string(self):
        assert validate_password_complexity("") is False


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

class TestPasswordHashing:
    def test_hash_and_verify(self):
        raw = "Secure@Pass1"
        hashed = get_password_hash(raw)
        assert hashed != raw
        assert verify_password(raw, hashed) is True

    def test_wrong_password_fails(self):
        hashed = get_password_hash("Correct@Pass1")
        assert verify_password("Wrong@Pass1", hashed) is False

    def test_weak_password_rejected(self):
        with pytest.raises(AuthenticationException):
            get_password_hash("weak")


# ---------------------------------------------------------------------------
# JWT token creation / decoding
# ---------------------------------------------------------------------------

class TestJWTTokens:
    def test_create_token_returns_string(self):
        token = create_token({"sub": "user-123"}, timedelta(minutes=15))
        assert isinstance(token, str)
        assert len(token) > 20

    def test_token_payload_contains_sub(self):
        token = create_token({"sub": "user-456"}, timedelta(minutes=15))
        payload = jwt.decode(
            token,
            os.getenv("SECRET_KEY"),
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False},
        )
        assert payload["sub"] == "user-456"

    def test_token_contains_standard_claims(self):
        token = create_token({"sub": "user-789"}, timedelta(minutes=15))
        payload = jwt.decode(
            token,
            os.getenv("SECRET_KEY"),
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False},
        )
        assert "exp" in payload
        assert "iat" in payload
        assert "jti" in payload
        assert payload["iss"] == settings.PROJECT_NAME

    def test_create_tokens_returns_two_tokens(self):
        access, refresh = create_tokens({"sub": "user-abc"})
        assert isinstance(access, str)
        assert isinstance(refresh, str)
        assert access != refresh


# ---------------------------------------------------------------------------
# CSRF tokens
# ---------------------------------------------------------------------------

class TestCSRFToken:
    def test_generate_csrf_token_is_uuid(self):
        token = generate_csrf_token()
        assert len(token) == 36  # UUID format

    def test_verify_csrf_matching(self):
        token = generate_csrf_token()
        assert verify_csrf_token(token, token) is True

    def test_verify_csrf_mismatch(self):
        assert verify_csrf_token("aaa", "bbb") is False

    def test_verify_csrf_empty_raises(self):
        with pytest.raises(SecurityException):
            verify_csrf_token("", "token")

    def test_verify_csrf_none_raises(self):
        with pytest.raises(SecurityException):
            verify_csrf_token(None, "token")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Email verification tokens
# ---------------------------------------------------------------------------

class TestEmailVerificationToken:
    def test_generate_returns_string(self):
        token = generate_email_verification_token("user-id-1")
        assert isinstance(token, str)

    def test_verify_roundtrip(self):
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        token = generate_email_verification_token(user_id)
        decoded_user_id = verify_email_verification_token(token)
        assert decoded_user_id == user_id

    def test_verify_invalid_token_raises(self):
        with pytest.raises(ValueError, match="Invalid or expired"):
            verify_email_verification_token("totally.invalid.token")

    def test_verify_wrong_scope_raises(self):
        """A normal access token should not pass email-verification scope check."""
        token = create_token({"sub": "user-1", "scope": "access"}, timedelta(minutes=5))
        with pytest.raises(ValueError, match="Invalid"):
            verify_email_verification_token(token)
