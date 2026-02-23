"""Tests for prompts."""

from mcp_server_ads.prompts.workflows import (
    citation_analysis,
    generate_bibliography,
    literature_review,
)


def test_literature_review():
    result = literature_review(topic="dark matter", year_range="2020-2025")
    assert "dark matter" in result
    assert "2020-2025" in result
    assert "ads_search" in result


def test_citation_analysis():
    result = citation_analysis(bibcodes="2016PhRvL.116f1102A, 1905AnP...322..891E")
    assert "2016PhRvL.116f1102A" in result
    assert "1905AnP" in result
    assert "ads_metrics" in result


def test_generate_bibliography():
    result = generate_bibliography(source="dark matter", format="bibtex")
    assert "bibtex" in result
    assert "dark matter" in result
