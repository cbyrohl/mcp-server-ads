"""Reference resolver tool: ads_resolve_reference."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from mcp_server_ads.client import ADSClient
from mcp_server_ads.formatting import format_reference_resolve
from mcp_server_ads.server import mcp


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    tags={"reference"},
)
async def ads_resolve_reference(
    references: Annotated[
        list[str],
        Field(
            description="List of free-text reference strings to resolve "
            "(e.g. ['Einstein 1905 Annalen der Physik 17 891'])"
        ),
    ],
    ctx: Context | None = None,
) -> str:
    """Resolve free-text reference strings to ADS bibcodes.

    Accepts human-readable reference strings and attempts to match them to
    records in ADS. Useful for identifying papers from partial citations.
    """
    client: ADSClient = ctx.lifespan_context["ads_client"]
    text = await client.post_raw(
        "/v1/reference/text",
        json={"reference": references},
    )
    return format_reference_resolve(text)
