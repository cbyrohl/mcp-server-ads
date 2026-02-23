"""ADS API error types."""

from __future__ import annotations


class ADSError(Exception):
    """Base error for ADS API issues."""


class ADSAuthError(ADSError):
    """Invalid or missing API token (HTTP 401)."""


class ADSNotFoundError(ADSError):
    """Requested resource not found (HTTP 404)."""


class ADSRateLimitError(ADSError):
    """Rate limit exhausted (HTTP 429)."""


class ADSServerError(ADSError):
    """ADS server error (HTTP 5xx)."""
