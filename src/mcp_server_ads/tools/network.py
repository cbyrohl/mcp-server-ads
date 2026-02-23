"""Network visualization tool: ads_network (author or paper)."""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp import Context
from pydantic import Field

from mcp_server_ads.client import ADSClient
from mcp_server_ads.formatting import format_author_network, format_paper_network
from mcp_server_ads.server import mcp


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    tags={"network"},
)
async def ads_network(
    bibcodes: Annotated[
        list[str],
        Field(description="List of bibcodes to build the network from"),
    ],
    type: Annotated[
        Literal["author", "paper"],
        Field(
            description="Network type: 'author' for collaboration groups, "
            "'paper' for citation clusters"
        ),
    ] = "author",
    ctx: Context | None = None,
) -> str:
    """Generate a collaboration or citation network from a set of papers.

    - author: Groups authors who frequently co-author together
    - paper: Clusters papers by shared references/citations to reveal sub-topics
    """
    client: ADSClient = ctx.lifespan_context["ads_client"]
    endpoint = f"/v1/vis/{type}-network"
    data = await client.post(endpoint, json={"bibcodes": bibcodes})
    if type == "author":
        return format_author_network(data)
    return format_paper_network(data)
