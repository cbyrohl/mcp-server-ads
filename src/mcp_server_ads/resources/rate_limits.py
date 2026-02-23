"""Live rate-limit status resource."""

from fastmcp import Context

from mcp_server_ads.client import ADSClient
from mcp_server_ads.server import mcp


@mcp.resource("ads://rate-limits")
def get_rate_limits(ctx: Context) -> str:
    """Current ADS API rate-limit status from tracked headers."""
    try:
        client: ADSClient = ctx.lifespan_context["ads_client"]
        return client.rate_limits.status_summary()
    except (KeyError, AttributeError):
        return "Rate limit data unavailable (no requests made yet)."
