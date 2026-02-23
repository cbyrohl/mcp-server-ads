"""Tests for the ADS HTTP client."""

from __future__ import annotations

import time

import httpx
import pytest

from mcp_server_ads.client import ADSClient, _raise_for_status
from mcp_server_ads.errors import (
    ADSAuthError,
    ADSNotFoundError,
    ADSRateLimitError,
    ADSServerError,
)


class TestRateLimitTracker:
    def test_initial_state(self, rate_limits):
        assert rate_limits.limit is None
        assert rate_limits.remaining is None
        assert not rate_limits.exhausted

    def test_update_from_headers(self, rate_limits):
        headers = httpx.Headers({
            "x-ratelimit-limit": "5000",
            "x-ratelimit-remaining": "4999",
            "x-ratelimit-reset": str(time.time() + 3600),
        })
        rate_limits.update(headers)
        assert rate_limits.limit == 5000
        assert rate_limits.remaining == 4999
        assert not rate_limits.exhausted

    def test_exhausted(self, rate_limits):
        headers = httpx.Headers({
            "x-ratelimit-limit": "5000",
            "x-ratelimit-remaining": "0",
            "x-ratelimit-reset": str(time.time() + 3600),
        })
        rate_limits.update(headers)
        assert rate_limits.exhausted

    def test_exhausted_but_reset_passed(self, rate_limits):
        headers = httpx.Headers({
            "x-ratelimit-limit": "5000",
            "x-ratelimit-remaining": "0",
            "x-ratelimit-reset": str(time.time() - 10),
        })
        rate_limits.update(headers)
        assert not rate_limits.exhausted

    def test_status_summary_no_data(self, rate_limits):
        assert "No rate-limit data" in rate_limits.status_summary()

    def test_status_summary_with_data(self, rate_limits):
        headers = httpx.Headers({
            "x-ratelimit-limit": "5000",
            "x-ratelimit-remaining": "4500",
            "x-ratelimit-reset": "1700000000",
        })
        rate_limits.update(headers)
        summary = rate_limits.status_summary()
        assert "4500/5000" in summary


class TestRaiseForStatus:
    def test_success(self):
        resp = httpx.Response(200, json={"ok": True})
        _raise_for_status(resp)  # should not raise

    def test_401(self):
        resp = httpx.Response(401, json={"error": "unauthorized"})
        with pytest.raises(ADSAuthError):
            _raise_for_status(resp)

    def test_404(self):
        resp = httpx.Response(404, json={"error": "not found"})
        with pytest.raises(ADSNotFoundError):
            _raise_for_status(resp)

    def test_429(self):
        resp = httpx.Response(429, json={"error": "rate limit"})
        with pytest.raises(ADSRateLimitError):
            _raise_for_status(resp)

    def test_500(self):
        resp = httpx.Response(500, json={"error": "internal"})
        with pytest.raises(ADSServerError):
            _raise_for_status(resp)


class TestADSClient:
    def test_create_no_token(self, monkeypatch):
        monkeypatch.delenv("ADS_API_TOKEN", raising=False)
        with pytest.raises(ADSAuthError):
            ADSClient.create(token="", base_url="https://api.adsabs.harvard.edu")

    @pytest.mark.asyncio
    async def test_get(self, ads_client, mock_httpx):
        mock_httpx.get("/v1/test").mock(
            return_value=httpx.Response(200, json={"result": "ok"}, headers={
                "x-ratelimit-limit": "5000",
                "x-ratelimit-remaining": "4999",
            })
        )
        data = await ads_client.get("/v1/test")
        assert data == {"result": "ok"}
        assert ads_client.rate_limits.remaining == 4999

    @pytest.mark.asyncio
    async def test_post(self, ads_client, mock_httpx):
        mock_httpx.post("/v1/test").mock(
            return_value=httpx.Response(200, json={"posted": True})
        )
        data = await ads_client.post("/v1/test", json={"foo": "bar"})
        assert data == {"posted": True}

    @pytest.mark.asyncio
    async def test_rate_limit_preflight(self, ads_client):
        ads_client.rate_limits.remaining = 0
        ads_client.rate_limits.reset = time.time() + 3600
        ads_client.rate_limits.limit = 5000
        from fastmcp.exceptions import ToolError
        with pytest.raises(ToolError):
            await ads_client.get("/v1/test")
