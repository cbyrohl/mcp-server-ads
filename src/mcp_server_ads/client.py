"""HTTP client for the ADS API with rate-limit tracking."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import httpx
from fastmcp.exceptions import ToolError

from mcp_server_ads.config import ADS_API_URL
from mcp_server_ads.errors import (
    ADSAuthError,
    ADSNotFoundError,
    ADSRateLimitError,
    ADSServerError,
)


@dataclass
class RateLimitTracker:
    """Tracks ADS API rate-limit headers."""

    limit: int | None = None
    remaining: int | None = None
    reset: float | None = None
    _last_updated: float = field(default_factory=time.monotonic)

    def update(self, headers: httpx.Headers) -> None:
        rl = headers.get("x-ratelimit-limit")
        rr = headers.get("x-ratelimit-remaining")
        rs = headers.get("x-ratelimit-reset")
        if rl is not None:
            self.limit = int(rl)
        if rr is not None:
            self.remaining = int(rr)
        if rs is not None:
            self.reset = float(rs)
        self._last_updated = time.monotonic()

    @property
    def exhausted(self) -> bool:
        if self.remaining is None:
            return False
        if self.remaining > 0:
            return False
        if self.reset is not None and time.time() > self.reset:
            return False
        return True

    def status_summary(self) -> str:
        if self.limit is None:
            return "No rate-limit data yet (no requests made)."
        remaining = self.remaining if self.remaining is not None else "?"
        return f"{remaining}/{self.limit} requests remaining (resets at epoch {self.reset})"


def _raise_for_status(response: httpx.Response) -> None:
    """Map ADS HTTP errors to typed exceptions."""
    if response.is_success:
        return
    code = response.status_code
    try:
        body = response.json()
        msg = body.get("error", response.text)
    except (ValueError, KeyError):
        msg = response.text
    if code == 401:
        raise ADSAuthError(f"Authentication failed: {msg}")
    if code == 404:
        raise ADSNotFoundError(f"Not found: {msg}")
    if code == 429:
        raise ADSRateLimitError(f"Rate limit exceeded: {msg}")
    if 500 <= code < 600:
        raise ADSServerError(f"ADS server error ({code}): {msg}")
    response.raise_for_status()


class ADSClient:
    """Async HTTP client for the ADS API."""

    def __init__(self, http: httpx.AsyncClient, rate_limits: RateLimitTracker | None = None):
        self._http = http
        self.rate_limits = rate_limits or RateLimitTracker()

    @classmethod
    def create(cls, token: str | None = None, base_url: str | None = None) -> ADSClient:
        import os

        token = token or os.environ.get("ADS_API_TOKEN", "")
        base_url = base_url or ADS_API_URL
        if not token:
            raise ADSAuthError("ADS_API_TOKEN environment variable is not set.")
        http = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=30.0,
        )
        return cls(http)

    def _check_rate_limit(self) -> None:
        if self.rate_limits.exhausted:
            raise ToolError(
                f"ADS rate limit exhausted. {self.rate_limits.status_summary()}"
            )

    async def get(self, path: str, **kwargs: Any) -> dict[str, Any]:
        self._check_rate_limit()
        resp = await self._http.get(path, **kwargs)
        self.rate_limits.update(resp.headers)
        _raise_for_status(resp)
        return resp.json()

    async def post(self, path: str, **kwargs: Any) -> dict[str, Any]:
        self._check_rate_limit()
        resp = await self._http.post(path, **kwargs)
        self.rate_limits.update(resp.headers)
        _raise_for_status(resp)
        return resp.json()

    async def put(self, path: str, **kwargs: Any) -> dict[str, Any]:
        self._check_rate_limit()
        resp = await self._http.put(path, **kwargs)
        self.rate_limits.update(resp.headers)
        _raise_for_status(resp)
        return resp.json()

    async def delete(self, path: str, **kwargs: Any) -> dict[str, Any]:
        self._check_rate_limit()
        resp = await self._http.delete(path, **kwargs)
        self.rate_limits.update(resp.headers)
        _raise_for_status(resp)
        return resp.json()

    async def post_raw(self, path: str, **kwargs: Any) -> str:
        """POST returning raw text (e.g. export endpoints)."""
        self._check_rate_limit()
        resp = await self._http.post(path, **kwargs)
        self.rate_limits.update(resp.headers)
        _raise_for_status(resp)
        return resp.text

    async def close(self) -> None:
        await self._http.aclose()
