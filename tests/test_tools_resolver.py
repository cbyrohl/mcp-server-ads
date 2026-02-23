"""Tests for resolver tool."""

from __future__ import annotations

import httpx
import pytest

from mcp_server_ads.tools.resolver import ads_resolve_links
from tests.conftest import load_fixture


@pytest.mark.asyncio
async def test_resolve_links(mock_ctx, mock_httpx):
    fixture = load_fixture("resolver_response.json")
    mock_httpx.get("/v1/resolver/2016PhRvL.116f1102A").mock(
        return_value=httpx.Response(200, json=fixture)
    )
    result = await ads_resolve_links(bibcode="2016PhRvL.116f1102A", ctx=mock_ctx)
    assert "arXiv" in result
    assert "Publisher" in result


@pytest.mark.asyncio
async def test_resolve_links_with_type(mock_ctx, mock_httpx):
    fixture = load_fixture("resolver_response.json")
    mock_httpx.get("/v1/resolver/2016PhRvL.116f1102A/esource").mock(
        return_value=httpx.Response(200, json=fixture)
    )
    result = await ads_resolve_links(
        bibcode="2016PhRvL.116f1102A", link_type="esource", ctx=mock_ctx,
    )
    assert "arXiv" in result
