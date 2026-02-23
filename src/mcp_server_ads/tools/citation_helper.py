"""Citation helper tool: ads_citation_helper."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from mcp_server_ads.client import ADSClient
from mcp_server_ads.formatting import format_citation_helper
from mcp_server_ads.server import mcp


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    tags={"citation_helper"},
)
async def ads_citation_helper(
    bibcodes: Annotated[
        list[str],
        Field(description="List of bibcodes already in the bibliography"),
    ],
    ctx: Context | None = None,
) -> str:
    """Suggest papers that should be cited alongside the given set.

    Given a set of bibcodes (e.g. from a paper's bibliography), the citation
    helper returns papers that are frequently co-cited with the input set
    but are not yet included.
    """
    client: ADSClient = ctx.lifespan_context["ads_client"]
    data = await client.post(
        "/v1/citation_helper",
        json={"bibcodes": bibcodes},
    )
    return format_citation_helper(data)
