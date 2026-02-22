"""
Unit tests for pagination schema and RBAC.

Covers:
- PaginatedResponse generic schema
- require_role dependency (role checks, admin access, forbidden for regular users)
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from httpx import AsyncClient

from app.schemas.base import PaginatedResponse
from app.domain.value_objects.enums import UserRole


class TestPaginatedResponse:
    """Verify PaginatedResponse schema construction."""

    def test_basic_page(self):
        resp = PaginatedResponse(
            items=["a", "b", "c"],
            total=10,
            skip=0,
            limit=3,
            has_more=True,
        )
        assert resp.items == ["a", "b", "c"]
        assert resp.total == 10
        assert resp.has_more is True

    def test_last_page(self):
        resp = PaginatedResponse(
            items=["x"],
            total=4,
            skip=3,
            limit=3,
            has_more=False,
        )
        assert resp.has_more is False
        assert resp.skip == 3

    def test_empty_page(self):
        resp = PaginatedResponse(
            items=[],
            total=0,
            skip=0,
            limit=10,
            has_more=False,
        )
        assert resp.items == []
        assert resp.total == 0


class TestUserRole:
    """Verify UserRole enum values."""

    def test_user_role_values(self):
        assert UserRole.USER.value == "user"
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.MODERATOR.value == "moderator"

    def test_from_string(self):
        assert UserRole("user") == UserRole.USER
        assert UserRole("admin") == UserRole.ADMIN


class TestRequireRole:
    """
    Test the require_role dependency factory.

    We import the factory and simulate different user roles to verify
    it raises 403 for insufficient permissions.
    """

    async def test_admin_passes(self, client: AsyncClient, test_user, auth_headers, db_session):
        """Admin role should be accepted when admin is required."""
        # Set user role to admin in the DB
        test_user.role = UserRole.ADMIN.value
        db_session.add(test_user)
        await db_session.commit()

        from app.api.deps import require_role

        checker = require_role(UserRole.ADMIN)
        # Call the inner dependency directly with the user
        result = await checker(current_user=test_user)
        assert result == test_user

    async def test_user_blocked_from_admin(self, test_user):
        """Regular user should be rejected from admin-only endpoint."""
        from app.api.deps import require_role
        from fastapi import HTTPException

        test_user.role = UserRole.USER.value
        checker = require_role(UserRole.ADMIN)

        with pytest.raises(HTTPException) as exc_info:
            await checker(current_user=test_user)
        assert exc_info.value.status_code == 403

    async def test_multi_role_accepted(self, test_user):
        """User with moderator role should pass when moderator is allowed."""
        from app.api.deps import require_role

        test_user.role = UserRole.MODERATOR.value
        checker = require_role(UserRole.ADMIN, UserRole.MODERATOR)
        result = await checker(current_user=test_user)
        assert result == test_user
