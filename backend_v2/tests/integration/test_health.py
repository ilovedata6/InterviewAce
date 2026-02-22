"""
Integration tests for health-check endpoints.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


class TestHealth:
    async def test_health_returns_healthy(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    async def test_ready_returns_status(self, client: AsyncClient):
        """
        In the test environment the readiness probe hits the *test* DB
        (in-memory SQLite) which should be reachable.
        """
        # Patch the async_engine used in health.py to use the test engine
        from tests.conftest import test_engine
        from unittest.mock import patch

        with patch("app.api.health.async_engine", test_engine):
            resp = await client.get("/ready")

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ready"
        assert data["checks"]["database"] == "ok"
