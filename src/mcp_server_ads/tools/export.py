"""Export tool: ads_export."""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp import Context
from pydantic import Field

from mcp_server_ads.client import ADSClient
from mcp_server_ads.formatting import format_export
from mcp_server_ads.server import mcp

EXPORT_FORMATS = Literal[
    "bibtex", "bibtexabs", "ads", "endnote", "medlars", "ris",
    "aastex", "icarus", "mnras", "soph",
    "dcxml", "refxml", "refabsxml", "votable",
    "rss",
    "ieee", "csl", "custom",
]


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    tags={"export", "core"},
)
async def ads_export(
    bibcodes: Annotated[
        list[str],
        Field(description="List of bibcodes to export"),
    ],
    format: Annotated[
        EXPORT_FORMATS,
        Field(
            description="Export format. Common choices: "
            "'bibtex', 'bibtexabs', 'aastex', 'ris', 'csl'"
        ),
    ] = "bibtex",
    sort: Annotated[
        str,
        Field(description="Sort order for the exported records. Default: 'date desc'"),
    ] = "date desc",
    journalformat: Annotated[
        Literal["AASTeX macro", "Journal Abbreviation", "Journal Full Name"] | None,
        Field(description="Journal name format (only for some export formats)"),
    ] = None,
    ctx: Context | None = None,
) -> str:
    """Export paper records in various citation formats.

    Supports 18+ formats including BibTeX, AASTeX, RIS, EndNote, CSL-JSON,
    Dublin Core XML, VOTable, and more. Returns formatted citation text.
    """
    client: ADSClient = ctx.lifespan_context["ads_client"]
    payload: dict = {"bibcode": bibcodes, "sort": [sort]}
    if journalformat:
        payload["journalformat"] = journalformat
    data = await client.post(f"/v1/export/{format}", json=payload)
    return format_export(data)
