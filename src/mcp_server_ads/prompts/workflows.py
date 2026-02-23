"""Pre-built prompt workflows for common ADS tasks."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from mcp_server_ads.server import mcp


@mcp.prompt()
def literature_review(
    topic: Annotated[str, Field(description="Research topic to review")],
    year_range: Annotated[
        str,
        Field(description="Year range (e.g. '2018-2025'). Default: '2020-2025'"),
    ] = "2020-2025",
) -> str:
    """Multi-step literature review workflow for a research topic."""
    return f"""\
Conduct a comprehensive literature review on "{topic}" using the ADS database.

Follow these steps:

1. **Initial Search**: Use ads_search to find recent papers on this topic:
   - Query: abs:"{topic}" year:{year_range} property:refereed
   - Sort by citation_count desc, get 20 results

2. **Identify Key Papers**: From the results, identify the 5-10 most influential papers
   (highest citation count, most relevant to the topic).

3. **Expand Search**: For the top 2-3 papers, use ads_search with the citations()
   functional operator to find papers that cite them, revealing recent follow-up work.

4. **Compute Metrics**: Use ads_metrics on the key papers to understand the field's
   impact and growth.

5. **Export Bibliography**: Use ads_export to export the final curated list in BibTeX format.

6. **Summarize**: Provide a structured summary including:
   - Key findings and trends
   - Most influential papers and authors
   - Recent developments
   - Gaps or open questions

Topic: {topic}
Year range: {year_range}
"""


@mcp.prompt()
def citation_analysis(
    bibcodes: Annotated[
        str,
        Field(description="Comma-separated list of bibcodes to analyze"),
    ],
) -> str:
    """Citation network analysis workflow for a set of papers."""
    bibcode_list = [b.strip() for b in bibcodes.split(",")]
    formatted = "\n".join(f"- `{b}`" for b in bibcode_list)
    return f"""\
Perform a citation network analysis on the following papers:

{formatted}

Follow these steps:

1. **Paper Details**: Use ads_bigquery to retrieve full metadata for all papers.

2. **Citation Metrics**: Use ads_metrics to compute citation statistics including
   h-index, citation counts, and read counts.

3. **Citation Network**: Use ads_network with type="paper" to visualize the paper network
   and identify clusters.

4. **Author Network**: Use ads_network with type="author" to identify key collaborator groups.

5. **Citation Suggestions**: Use ads_citation_helper to find related papers
   that should be cited.

6. **Summarize**: Provide analysis including:
   - Citation count distribution
   - Key metric indicators (h-index, etc.)
   - Network clusters and their themes
   - Suggested additional references
"""


@mcp.prompt()
def generate_bibliography(
    source: Annotated[
        str,
        Field(
            description="Either a search query or comma-separated bibcodes"
        ),
    ],
    format: Annotated[
        str,
        Field(description="Export format (bibtex, aastex, ris, etc.). Default: bibtex"),
    ] = "bibtex",
) -> str:
    """Generate a formatted bibliography from a search or bibcode list."""
    return f"""\
Generate a formatted bibliography from the following source.

Source: {source}

Steps:

1. **Resolve Papers**:
   - If the source looks like bibcodes (contains slashes or dots typical of bibcodes),
     use ads_bigquery to verify them.
   - Otherwise, use ads_search to find matching papers.

2. **Review Results**: Show the papers found and confirm they are the intended ones.

3. **Export**: Use ads_export with format="{format}" to generate the bibliography.

4. **Deliver**: Return the formatted bibliography ready for use.

Requested format: {format}
"""
