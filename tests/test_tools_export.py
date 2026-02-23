"""Tests for export tool."""

from __future__ import annotations

import httpx
import pytest

from mcp_server_ads.tools.export import ads_export
from tests.conftest import load_fixture


@pytest.mark.asyncio
async def test_ads_export_bibtex(mock_ctx, mock_httpx):
    fixture = load_fixture("export_response.json")
    mock_httpx.post("/v1/export/bibtex").mock(
        return_value=httpx.Response(200, json=fixture)
    )
    result = await ads_export(
        bibcodes=["1905AnP...322..891E"], format="bibtex", ctx=mock_ctx,
    )
    assert "@ARTICLE" in result
    assert "Einstein" in result
