"""Tests for metrics tool."""

from __future__ import annotations

import httpx
import pytest

from mcp_server_ads.tools.metrics import ads_metrics
from tests.conftest import load_fixture


@pytest.mark.asyncio
async def test_ads_metrics(mock_ctx, mock_httpx):
    fixture = load_fixture("metrics_response.json")
    mock_httpx.post("/v1/metrics").mock(
        return_value=httpx.Response(200, json=fixture)
    )
    result = await ads_metrics(
        bibcodes=["1905AnP...322..891E"], ctx=mock_ctx,
    )
    assert "h-index" in result
    assert "35" in result
