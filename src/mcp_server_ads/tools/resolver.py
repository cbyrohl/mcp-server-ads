"""Link resolver tool: ads_resolve_links."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from mcp_server_ads.client import ADSClient
from mcp_server_ads.formatting import format_resolver_links
from mcp_server_ads.server import mcp


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    tags={"resolver"},
)
async def ads_resolve_links(
    bibcode: Annotated[str, Field(description="Bibcode to resolve links for")],
    link_type: Annotated[
        str | None,
        Field(
            description="Specific link type to resolve (e.g. 'esource', 'data', 'citation', "
            "'reference', 'coreads'). If omitted, returns all available links."
        ),
    ] = None,
    ctx: Context | None = None,
) -> str:
    """Resolve available links for a paper (full text, data, citations, etc.)."""
    client: ADSClient = ctx.lifespan_context["ads_client"]
    path = f"/v1/resolver/{bibcode}"
    if link_type:
        path += f"/{link_type}"
    data = await client.get(path)
    return format_resolver_links(data)
