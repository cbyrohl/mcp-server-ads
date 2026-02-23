"""Metrics tool: ads_metrics."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from mcp_server_ads.client import ADSClient
from mcp_server_ads.formatting import format_metrics
from mcp_server_ads.server import mcp


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    tags={"metrics", "core"},
)
async def ads_metrics(
    bibcodes: Annotated[
        list[str],
        Field(description="List of bibcodes to compute metrics for"),
    ],
    types: Annotated[
        list[str],
        Field(
            description="Metric types to compute. Options: 'basic', 'citations', "
            "'indicators', 'histograms'. Default: all."
        ),
    ] = ["basic", "citations", "indicators", "histograms"],
    ctx: Context | None = None,
) -> str:
    """Compute citation metrics for a set of papers.

    Returns h-index, g-index, i10-index, citation counts, read counts,
    and time-series histograms. Works for 1 to ~2000 bibcodes.
    """
    client: ADSClient = ctx.lifespan_context["ads_client"]
    data = await client.post(
        "/v1/metrics",
        json={"bibcodes": bibcodes, "types": types},
    )
    return format_metrics(data)
