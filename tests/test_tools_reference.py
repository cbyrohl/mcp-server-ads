"""Tests for reference resolver tool."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from mcp_server_ads.tools.reference import ads_resolve_reference

FIXTURE_TEXT = (Path(__file__).parent / "fixtures" / "reference_response.txt").read_text()


@pytest.mark.asyncio
async def test_resolve_reference(mock_ctx, mock_httpx):
    mock_httpx.post("/v1/reference/text").mock(
        return_value=httpx.Response(200, text=FIXTURE_TEXT)
    )
    result = await ads_resolve_reference(
        references=["Einstein 1905 Annalen der Physik 17 891"], ctx=mock_ctx,
    )
    assert "1905AnP" in result
    assert "Einstein" in result
