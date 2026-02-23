"""Shared test fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
import respx

from mcp_server_ads.client import ADSClient, RateLimitTracker

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES_DIR / name).read_text())


@pytest.fixture
def rate_limits():
    return RateLimitTracker()


@pytest.fixture
def mock_httpx():
    """Provide a respx-mocked httpx.AsyncClient."""
    with respx.mock(base_url="https://api.adsabs.harvard.edu") as mock:
        yield mock


@pytest.fixture
def ads_client(mock_httpx):
    """ADSClient backed by a respx-mocked transport."""
    http = httpx.AsyncClient(
        base_url="https://api.adsabs.harvard.edu",
        headers={"Authorization": "Bearer test-token"},
        timeout=5.0,
    )
    return ADSClient(http)


@pytest.fixture
def mock_ctx(ads_client):
    """Fake FastMCP Context that provides ads_client via lifespan_context."""
    ctx = MagicMock()
    ctx.lifespan_context = {"ads_client": ads_client}
    ctx.info = AsyncMock()
    ctx.warning = AsyncMock()
    ctx.error = AsyncMock()
    ctx.report_progress = AsyncMock()
    return ctx
