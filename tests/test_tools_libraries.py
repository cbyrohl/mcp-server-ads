"""Tests for consolidated library tools."""

from __future__ import annotations

import httpx
import pytest

from mcp_server_ads.tools.libraries import ads_library, ads_library_documents
from tests.conftest import load_fixture


@pytest.mark.asyncio
async def test_library_list(mock_ctx, mock_httpx):
    fixture = load_fixture("libraries_response.json")
    mock_httpx.get("/v1/biblib/libraries").mock(
        return_value=httpx.Response(200, json=fixture)
    )
    result = await ads_library(action="list", ctx=mock_ctx)
    assert "My Reading List" in result
    assert "Dark Matter" in result


@pytest.mark.asyncio
async def test_library_get(mock_ctx, mock_httpx):
    fixture = load_fixture("library_detail_response.json")
    mock_httpx.get("/v1/biblib/libraries/abc123").mock(
        return_value=httpx.Response(200, json=fixture)
    )
    result = await ads_library(action="get", library_id="abc123", ctx=mock_ctx)
    assert "My Reading List" in result
    assert "1905AnP" in result


@pytest.mark.asyncio
async def test_library_create(mock_ctx, mock_httpx):
    mock_httpx.post("/v1/biblib/libraries").mock(
        return_value=httpx.Response(200, json={"id": "new123"})
    )
    result = await ads_library(action="create", name="Test Lib", ctx=mock_ctx)
    assert "new123" in result
    assert "Test Lib" in result


@pytest.mark.asyncio
async def test_library_edit(mock_ctx, mock_httpx):
    mock_httpx.put("/v1/biblib/documents/abc123").mock(
        return_value=httpx.Response(200, json={"msg": "updated"})
    )
    result = await ads_library(
        action="edit", library_id="abc123", name="New Name", ctx=mock_ctx,
    )
    assert "abc123" in result


@pytest.mark.asyncio
async def test_library_delete(mock_ctx, mock_httpx):
    mock_httpx.delete("/v1/biblib/documents/abc123").mock(
        return_value=httpx.Response(200, json={})
    )
    result = await ads_library(action="delete", library_id="abc123", ctx=mock_ctx)
    assert "deleted" in result


@pytest.mark.asyncio
async def test_library_documents_add(mock_ctx, mock_httpx):
    mock_httpx.post("/v1/biblib/documents/abc123").mock(
        return_value=httpx.Response(200, json={"number_added": 2})
    )
    result = await ads_library_documents(
        library_id="abc123", action="add",
        bibcodes=["1905AnP...322..891E", "1916AnP...354..769E"],
        ctx=mock_ctx,
    )
    assert "2" in result


@pytest.mark.asyncio
async def test_library_documents_union(mock_ctx, mock_httpx):
    mock_httpx.post("/v1/biblib/libraries/operations/abc123").mock(
        return_value=httpx.Response(200, json={"name": "Merged", "description": "ok"})
    )
    result = await ads_library_documents(
        library_id="abc123", action="union", libraries=["def456"], ctx=mock_ctx,
    )
    assert "union" in result


@pytest.mark.asyncio
async def test_library_documents_get_notes(mock_ctx, mock_httpx):
    mock_httpx.get("/v1/biblib/notes/abc123").mock(
        return_value=httpx.Response(200, json=[
            {"bibcode": "1905AnP...322..891E", "content": "Great paper"},
        ])
    )
    result = await ads_library_documents(
        library_id="abc123", action="get_notes", ctx=mock_ctx,
    )
    assert "Great paper" in result
