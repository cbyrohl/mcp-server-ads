"""Tests for objects tool."""

from __future__ import annotations

import httpx
import pytest

from mcp_server_ads.tools.objects import ads_object_search
from tests.conftest import load_fixture


@pytest.mark.asyncio
async def test_object_search(mock_ctx, mock_httpx):
    fixture = load_fixture("objects_response.json")
    mock_httpx.post("/v1/objects").mock(
        return_value=httpx.Response(200, json=fixture)
    )
    result = await ads_object_search(identifiers=["M31", "NGC 1234"], ctx=mock_ctx)
    assert "simbid" in result
