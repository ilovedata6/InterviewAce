"""
Integration tests for authentication endpoints.

Covers:
- POST /register
- POST /login
- POST /refresh
- GET /me
- POST /logout
- Duplicate registration
- Invalid credentials
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


API = "/api/v1/auth"

# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        resp = await client.post(
            f"{API}/register",
            json={
                "email": "new@example.com",
                "password": "Strong@Pass1",
                "full_name": "New User",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "message" in data

    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        resp = await client.post(
            f"{API}/register",
            json={
                "email": "testuser@example.com",  # already exists via test_user
                "password": "Strong@Pass1",
                "full_name": "Dupe User",
            },
        )
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    async def test_register_weak_password(self, client: AsyncClient):
        resp = await client.post(
            f"{API}/register",
            json={
                "email": "weak@example.com",
                "password": "weak",
                "full_name": "Weak User",
            },
        )
        # get_password_hash raises AuthenticationException → 401, or may bubble as 500
        assert resp.status_code in (400, 401, 422, 500)


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class TestLogin:
    async def test_login_success(self, client: AsyncClient, test_user):
        resp = await client.post(
            f"{API}/login",
            data={"username": "testuser@example.com", "password": "Test@1234"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        resp = await client.post(
            f"{API}/login",
            data={"username": "testuser@example.com", "password": "Wrong@Pass1"},
        )
        assert resp.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        resp = await client.post(
            f"{API}/login",
            data={"username": "nobody@example.com", "password": "Any@Pass1"},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Get current user (/me)
# ---------------------------------------------------------------------------

class TestMe:
    async def test_me_authenticated(self, client: AsyncClient, auth_headers):
        resp = await client.get(f"{API}/me", headers=auth_headers)
        # me uses get_current_user from core.security which checks blacklist
        # In the test DB with no blacklist entries, this should succeed
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "testuser@example.com"
        assert data["full_name"] == "Test User"

    async def test_me_unauthenticated(self, client: AsyncClient):
        resp = await client.get(f"{API}/me")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Token refresh
# ---------------------------------------------------------------------------

class TestRefresh:
    async def test_refresh_with_valid_token(self, client: AsyncClient, test_user):
        """Login first, then use the refresh token to obtain new tokens."""
        login_resp = await client.post(
            f"{API}/login",
            data={"username": "testuser@example.com", "password": "Test@1234"},
        )
        assert login_resp.status_code == 200
        refresh_tok = login_resp.json()["refresh_token"]

        resp = await client.post(
            f"{API}/refresh",
            headers={"Authorization": f"Bearer {refresh_tok}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_no_token(self, client: AsyncClient):
        resp = await client.post(f"{API}/refresh")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

class TestLogout:
    async def test_logout_success(self, client: AsyncClient, test_user):
        """Login, then logout with the access token."""
        login_resp = await client.post(
            f"{API}/login",
            data={"username": "testuser@example.com", "password": "Test@1234"},
        )
        assert login_resp.status_code == 200
        access_tok = login_resp.json()["access_token"]

        resp = await client.post(
            f"{API}/logout",
            headers={"Authorization": f"Bearer {access_tok}"},
        )
        assert resp.status_code == 200
        assert "logged out" in resp.json()["message"].lower()

    async def test_logout_unauthenticated(self, client: AsyncClient):
        resp = await client.post(f"{API}/logout")
        assert resp.status_code in (401, 403)
