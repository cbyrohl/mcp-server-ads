"""Tests for search tools."""

from __future__ import annotations

import httpx
import pytest

from mcp_server_ads.tools.search import ads_bigquery, ads_search
from tests.conftest import load_fixture


@pytest.mark.asyncio
async def test_ads_search(mock_ctx, mock_httpx):
    fixture = load_fixture("search_response.json")
    mock_httpx.get("/v1/search/query").mock(
        return_value=httpx.Response(200, json=fixture)
    )
    result = await ads_search(query='author:"Einstein"', ctx=mock_ctx)
    assert "150" in result
    assert "Einstein" in result


@pytest.mark.asyncio
async def test_ads_search_custom_fields(mock_ctx, mock_httpx):
    fixture = load_fixture("search_response.json")
    mock_httpx.get("/v1/search/query").mock(
        return_value=httpx.Response(200, json=fixture)
    )
    result = await ads_search(
        query="test", fields="bibcode,title", sort="citation_count desc",
        rows=5, start=0, ctx=mock_ctx,
    )
    assert "Einstein" in result


@pytest.mark.asyncio
async def test_ads_bigquery(mock_ctx, mock_httpx):
    fixture = load_fixture("search_response.json")
    mock_httpx.post("/v1/search/bigquery").mock(
        return_value=httpx.Response(200, json=fixture)
    )
    result = await ads_bigquery(
        bibcodes=["1905AnP...322..891E", "1916AnP...354..769E"],
        ctx=mock_ctx,
    )
    assert "150" in result
