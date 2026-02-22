"""
Integration tests for health-check endpoints.
"""

from __future__ import annotations

import pytest
from unittest.mock import patch, AsyncMock
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
        Redis is mocked to return a successful ping.
        """
        # Patch the async_engine used in health.py to use the test engine
        from tests.conftest import test_engine

        # Create a mock Redis client that returns True for ping()
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_get_redis = AsyncMock(return_value=mock_redis)

        with (
            patch("app.api.health.async_engine", test_engine),
            patch("app.api.health.get_redis", mock_get_redis),
        ):
            resp = await client.get("/ready")

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ready"
        assert data["checks"]["database"] == "ok"
        assert data["checks"]["redis"] == "ok"

    async def test_ready_redis_down(self, client: AsyncClient):
        """
        When Redis is unreachable, /ready should report not_ready (503).
        """
        from tests.conftest import test_engine

        mock_get_redis = AsyncMock(side_effect=ConnectionError("Redis down"))

        with (
            patch("app.api.health.async_engine", test_engine),
            patch("app.api.health.get_redis", mock_get_redis),
        ):
            resp = await client.get("/ready")

        assert resp.status_code == 503
        data = resp.json()
        assert data["status"] == "not_ready"
        assert data["checks"]["redis"] == "unavailable"
