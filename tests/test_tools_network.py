"""Tests for consolidated network tool."""

from __future__ import annotations

import httpx
import pytest

from mcp_server_ads.tools.network import ads_network
from tests.conftest import load_fixture


@pytest.mark.asyncio
async def test_author_network(mock_ctx, mock_httpx):
    fixture = load_fixture("author_network_response.json")
    mock_httpx.post("/v1/vis/author-network").mock(
        return_value=httpx.Response(200, json=fixture)
    )
    result = await ads_network(
        bibcodes=["1905AnP...322..891E"], type="author", ctx=mock_ctx,
    )
    assert "Einstein" in result
    assert "Bohr" in result


@pytest.mark.asyncio
async def test_paper_network(mock_ctx, mock_httpx):
    fixture = load_fixture("paper_network_response.json")
    mock_httpx.post("/v1/vis/paper-network").mock(
        return_value=httpx.Response(200, json=fixture)
    )
    result = await ads_network(
        bibcodes=["1905AnP...322..891E"], type="paper", ctx=mock_ctx,
    )
    assert "Gravitational Waves" in result
