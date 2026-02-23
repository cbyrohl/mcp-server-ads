"""Tests for citation helper tool."""

from __future__ import annotations

import httpx
import pytest

from mcp_server_ads.tools.citation_helper import ads_citation_helper
from tests.conftest import load_fixture


@pytest.mark.asyncio
async def test_citation_helper(mock_ctx, mock_httpx):
    fixture = load_fixture("citation_helper_response.json")
    mock_httpx.post("/v1/citation_helper").mock(
        return_value=httpx.Response(200, json=fixture)
    )
    result = await ads_citation_helper(
        bibcodes=["2016PhRvL.116f1102A"], ctx=mock_ctx,
    )
    assert "2017ApJ" in result
    assert "2.00" in result
