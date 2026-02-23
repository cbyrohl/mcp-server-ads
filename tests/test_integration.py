"""Integration tests against the live ADS API.

Skipped unless ADS_API_TOKEN is set in the environment.
Run with: ADS_API_TOKEN=your-token uv run pytest tests/test_integration.py -v
"""

from __future__ import annotations

import os

import pytest

from mcp_server_ads.client import ADSClient

pytestmark = [
    pytest.mark.skipif(
        not os.environ.get("ADS_API_TOKEN"),
        reason="ADS_API_TOKEN not set",
    ),
    pytest.mark.integration,
]

# A well-known paper that won't disappear from ADS
LIGO_BIBCODE = "2016PhRvL.116f1102A"
EINSTEIN_BIBCODE = "1905AnP...322..891E"


@pytest.fixture
async def client():
    c = ADSClient.create()
    try:
        yield c
    finally:
        await c.close()


# --- Search ---


class TestSearch:
    async def test_search_by_bibcode(self, client):
        data = await client.get(
            "/v1/search/query",
            params={"q": f"bibcode:{LIGO_BIBCODE}", "fl": "bibcode,title", "rows": 1},
        )
        assert data["response"]["numFound"] >= 1
        assert data["response"]["docs"][0]["bibcode"] == LIGO_BIBCODE

    async def test_search_by_author(self, client):
        data = await client.get(
            "/v1/search/query",
            params={"q": 'author:"Einstein, A"', "fl": "bibcode", "rows": 5},
        )
        assert data["response"]["numFound"] > 0

    async def test_bigquery(self, client):
        bibcodes = [LIGO_BIBCODE, EINSTEIN_BIBCODE]
        bibcode_block = "bibcode\n" + "\n".join(bibcodes)
        data = await client.post(
            "/v1/search/bigquery",
            params={"q": "*:*", "fl": "bibcode,title", "rows": 10},
            content=bibcode_block,
            headers={"Content-Type": "big-query/csv"},
        )
        found_bibcodes = {d["bibcode"] for d in data["response"]["docs"]}
        assert LIGO_BIBCODE in found_bibcodes


# --- Export ---


class TestExport:
    async def test_export_bibtex(self, client):
        data = await client.post(
            "/v1/export/bibtex",
            json={"bibcode": [LIGO_BIBCODE], "sort": ["date desc"]},
        )
        export = data.get("export", "")
        assert "ARTICLE" in export or "article" in export.lower()
        assert "2016" in export

    async def test_export_ris(self, client):
        data = await client.post(
            "/v1/export/ris",
            json={"bibcode": [LIGO_BIBCODE], "sort": ["date desc"]},
        )
        export = data.get("export", "")
        assert "TY  -" in export


# --- Metrics ---


class TestMetrics:
    async def test_metrics(self, client):
        data = await client.post(
            "/v1/metrics",
            json={"bibcodes": [LIGO_BIBCODE], "types": ["basic", "indicators"]},
        )
        assert "basic stats" in data
        basic = data["basic stats"]
        assert basic["number of papers"] >= 1
        assert basic["total number of reads"] > 0

        assert "indicators" in data
        assert data["indicators"]["h"] >= 1


# --- Resolver ---


class TestResolver:
    async def test_resolve_links(self, client):
        data = await client.get(f"/v1/resolver/{LIGO_BIBCODE}")
        links = data.get("links", {})
        assert links.get("count", 0) > 0 or len(links.get("records", [])) > 0


# --- Objects ---


class TestObjects:
    @pytest.mark.xfail(reason="SIMBAD/NED upstream may be temporarily unavailable")
    async def test_object_search(self, client):
        data = await client.post(
            "/v1/objects",
            json={"identifiers": ["M31"]},
        )
        assert "query" in data


# --- Citation Helper ---


class TestCitationHelper:
    async def test_citation_helper(self, client):
        data = await client.post(
            "/v1/citation_helper",
            json={"bibcodes": [LIGO_BIBCODE]},
        )
        # API returns a plain list of suggestions
        assert isinstance(data, list)
        assert len(data) > 0
        assert "bibcode" in data[0]


# --- Reference ---


class TestReference:
    async def test_resolve_reference(self, client):
        text = await client.post_raw(
            "/v1/reference/text",
            json={"reference": ["Einstein 1905 Annalen der Physik 17 891"]},
        )
        assert "1905AnP" in text


# --- Networks ---


class TestNetworks:
    async def test_author_network(self, client):
        data = await client.post(
            "/v1/vis/author-network",
            json={"bibcodes": [LIGO_BIBCODE, EINSTEIN_BIBCODE]},
        )
        assert "data" in data

    async def test_paper_network(self, client):
        data = await client.post(
            "/v1/vis/paper-network",
            json={"bibcodes": [LIGO_BIBCODE, EINSTEIN_BIBCODE]},
        )
        assert "data" in data


# --- Rate Limits ---


class TestRateLimits:
    async def test_rate_limits_tracked(self, client):
        await client.get(
            "/v1/search/query",
            params={"q": f"bibcode:{LIGO_BIBCODE}", "fl": "bibcode", "rows": 1},
        )
        assert client.rate_limits.limit is not None
        assert client.rate_limits.remaining is not None
        assert client.rate_limits.remaining > 0
