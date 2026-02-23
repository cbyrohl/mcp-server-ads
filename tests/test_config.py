"""Tests for config module."""


def test_default_api_url():
    from mcp_server_ads.config import ADS_API_URL
    assert "adsabs.harvard.edu" in ADS_API_URL
