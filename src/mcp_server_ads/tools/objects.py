"""Object search tool: ads_object_search (SIMBAD/NED integration)."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from mcp_server_ads.client import ADSClient
from mcp_server_ads.formatting import format_object_results
from mcp_server_ads.server import mcp


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    tags={"objects"},
)
async def ads_object_search(
    identifiers: Annotated[
        list[str],
        Field(description="List of astronomical object identifiers (e.g. ['M31', 'NGC 1234'])"),
    ],
    ctx: Context | None = None,
) -> str:
    """Translate astronomical object names to ADS search queries via SIMBAD/NED.

    Provide object identifiers (e.g. 'M31', 'Crab Nebula', 'NGC 1234') and get
    back an ADS query that matches papers about those objects.
    """
    client: ADSClient = ctx.lifespan_context["ads_client"]
    data = await client.post(
        "/v1/objects",
        json={"identifiers": identifiers},
    )
    return format_object_results(data)
