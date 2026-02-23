"""FastMCP server definition and lifespan."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastmcp import FastMCP

from mcp_server_ads.client import ADSClient


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Create and tear down the shared ADS HTTP client."""
    client = ADSClient.create()
    try:
        yield {"ads_client": client}
    finally:
        await client.close()


mcp = FastMCP(
    "NASA ADS",
    instructions=(
        "MCP server for the NASA Astrophysics Data System (ADS). "
        "Use ads_search as the primary entry point — it supports field queries "
        "(author, title, abs, year), boolean operators, and functional operators "
        "like citations(bibcode:...) to find papers that cite a given paper, "
        "references(bibcode:...) to find its references, and similar()/trending()/reviews(). "
        "Use ads_export to generate BibTeX or other citation formats. "
        "Use ads_metrics for h-index and citation statistics. "
        "Read the ads://syntax resource for the full query syntax reference."
    ),
    lifespan=lifespan,
)

# Register tools, resources, and prompts by importing submodules.
import mcp_server_ads.prompts  # noqa: E402, F401
import mcp_server_ads.resources  # noqa: E402, F401
import mcp_server_ads.tools  # noqa: E402, F401


def main() -> None:
    mcp.run()
