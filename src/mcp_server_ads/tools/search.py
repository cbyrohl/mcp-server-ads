"""Search tools: ads_search and ads_bigquery."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from mcp_server_ads.client import ADSClient
from mcp_server_ads.formatting import format_search_results
from mcp_server_ads.server import mcp

DEFAULT_FIELDS = "bibcode,title,author,year,pub,citation_count,identifier"

# Operators that expand into weighted OR-queries matching most of the corpus;
# their results are only meaningful ranked by relevance.
RELEVANCE_OPERATORS = ("similar(", "useful(", "trending(")


def _default_sort(query: str) -> str:
    if any(op in query.lower() for op in RELEVANCE_OPERATORS):
        return "score desc"
    return "date desc"


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    tags={"search", "core"},
)
async def ads_search(
    query: Annotated[
        str,
        Field(description="ADS search query (e.g. 'author:\"Einstein\" year:1905')"),
    ],
    fields: Annotated[
        str,
        Field(
            description="Comma-separated list of fields to return. "
            "Add 'abstract' for paper summaries. "
            "Default: bibcode,title,author,year,pub,citation_count,identifier",
        ),
    ] = DEFAULT_FIELDS,
    sort: Annotated[
        str | None,
        Field(
            description="Sort order (e.g. 'citation_count desc', 'date desc'). "
            "Default: 'date desc', or 'score desc' for queries using "
            "similar()/useful()/trending()"
        ),
    ] = None,
    rows: Annotated[
        int,
        Field(description="Number of results to return (1-200). Default: 10", ge=1, le=200),
    ] = 10,
    start: Annotated[
        int,
        Field(description="Starting index for pagination. Default: 0", ge=0),
    ] = 0,
    ctx: Context | None = None,
) -> str:
    """Search the NASA ADS database.

    Supports the full ADS query syntax including field-qualified searches,
    boolean operators, and functional operators.

    Common query patterns:
    - author:"Einstein, A" year:1905
    - title:"dark matter" property:refereed
    - abs:"gravitational waves" database:astronomy

    To find citations and references of a paper:
    - citations(bibcode:2016PhRvL.116f1102A) — papers that cite it
    - references(bibcode:2016PhRvL.116f1102A) — papers it cites

    Other functional operators:
    - trending(abs:"exoplanet") — trending papers
    - reviews(abs:"dark matter") — review articles
    - useful(bibcode:2016PhRvL.116f1102A) — related useful papers
    - similar(bibcode:2016PhRvL.116f1102A) — similar papers

    Note: similar()/useful()/trending() expand into broad weighted queries,
    so their total hit counts are not meaningful; only the top relevance-ranked
    results matter.
    """
    client: ADSClient = ctx.lifespan_context["ads_client"]
    if sort is None:
        sort = _default_sort(query)
    data = await client.get(
        "/v1/search/query",
        params={
            "q": query,
            "fl": fields,
            "sort": sort,
            "rows": rows,
            "start": start,
        },
    )
    return format_search_results(data)


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    tags={"search", "core"},
)
async def ads_bigquery(
    bibcodes: Annotated[
        list[str],
        Field(description="List of bibcodes to search within"),
    ],
    query: Annotated[
        str,
        Field(description="ADS query to apply to the bibcode set. Use '*:*' for no filter."),
    ] = "*:*",
    fields: Annotated[
        str,
        Field(description="Comma-separated fields to return"),
    ] = DEFAULT_FIELDS,
    sort: Annotated[
        str,
        Field(description="Sort order. Default: 'date desc'"),
    ] = "date desc",
    rows: Annotated[
        int,
        Field(description="Number of results (1-200). Default: 10", ge=1, le=200),
    ] = 10,
    ctx: Context | None = None,
) -> str:
    """Search within a specific set of bibcodes (big-query).

    Useful for filtering, sorting, or retrieving metadata for a known set of papers.
    Provide up to 2000 bibcodes at once.
    """
    client: ADSClient = ctx.lifespan_context["ads_client"]
    bibcode_block = "bibcode\n" + "\n".join(bibcodes)
    data = await client.post(
        "/v1/search/bigquery",
        params={
            "q": query,
            "fl": fields,
            "sort": sort,
            "rows": rows,
        },
        content=bibcode_block,
        headers={"Content-Type": "big-query/csv"},
    )
    return format_search_results(data)
